from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression

import logging



_logger = logging.getLogger(__name__)


class OrdMain(models.Model):
    _name = 'ord.main'
    _description = 'Order main'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'

    status = fields.Selection([
        ('waiting', 'Waiting'),
        ('refused', 'Refused'),
        ('accepted', 'Accepted'),
    ], default='waiting', string='Order status', tracking=True)

    reference = fields.Char(
        string='Reference',
        size=50,
        readonly=True,
        default='TBD',
        copy=False,
        )

    creation_date = fields.Datetime(string='Creation date', required=True, default=fields.Datetime.now)
    owner_id = fields.Many2one('res.users', string='Owner', required=True, default=lambda self: self.env.user)
    department_id = fields.Many2one('base_act.department',
                                    string='Department',
                                    required=True,
                                    tracking=True,
                                    default=lambda self: self._get_default_department())
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        required=True,
        domain="[('groups_id.name', '=', 'odoo_order_approver')]"
    )

    ticket_subject = fields.Char(
        string='Request Subject',
        help='What do you need?',
        required=True,
    )
    ticket_description = fields.Text(
        string='Request Justification',
        help='Explain why you need this order and provide any relevant details.',
    )

    supplier_id = fields.Many2one(
        'ord.supplier',
        string='Supplier',
        required=True,
        domain="[('status_id.status', 'in', ['approved', 'new'])]"
    )


    type = fields.Selection([
        ('material', 'Material'),
        ('service', 'Service')
    ], string = 'Order type', required=True, default='material')

    attachment_ids = fields.One2many('ord.attachment', 'order_id', string='Attachments')

    viewer_ids = fields.Many2many(
        'res.groups',
        string='Viewers',
        compute='_compute_viewer_ids',
        store=True,
        help='Groups that can view this order'
    )

    is_delivered = fields.Boolean(string="Delivered", default=False)
    delivery_date = fields.Date(string='Delivery date')

    @api.onchange('is_delivered')
    def _onchange_is_delivered(self):
        if self.is_delivered:
            self.delivery_date = fields.Date.today()
        else:
            self.delivery_date = False

    @api.depends('new_ticket_subject', 'new_ticket_description')
    def _compute_ticket(self):
        for order in self:
            order.new_ticket_subject = order.ticket_id.subject
            order.new_ticket_description = order.ticket_id.description

    @api.depends('department_id', 'owner_id')
    def _compute_viewer_ids(self):
        for record in self:
            viewer_groups = self.env['res.groups']

            # if record.department_id and record.department_id.viewer_group_id:
            #     viewer_groups += record.department_id

            management_groups = self.env['res.groups'].search([
                ('name', 'in', ['Order Director', 'Order Approver'])
            ])
            viewer_groups += management_groups
            record.viewer_ids = viewer_groups

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', '/') == '/':

                vals['reference'] = self.env['ir.sequence'].next_by_code('ord.main.sequence') or '/'

        records = super().create(vals_list)

        # Only send notifications if we're not installing/updating modules
        if not self.env.context.get('install_mode') and not self._context.get('module_installation'):
            for record in records:
                record._send_approval_notification()

        return records

    def _send_approval_notification(self):
        """Send approval notification email"""
        self.ensure_one()

        if not self.approver_id or not self.approver_id.email:
            _logger.warning(f'No approver or approver email for order {self.reference}')
            return

        try:
            attachment_ids = []
            if self.attachment_ids:
                for attachment in self.attachment_ids:
                    mail_attachment = self.env['ir.attachment'].create({
                        'name': attachment.name,
                        'datas': attachment.datas,
                        'mimetype': attachment.mimetype,
                        'res_model': 'mail.mail',
                        'res_id': 0,
                    })
                    attachment_ids.append(mail_attachment.id)

            template = self.env.ref('order.mail_template_new_order_approval', raise_if_not_found=False)

            if template:
                template.send_mail(
                    self.id,
                    force_send=True,
                    email_values={
                        'email_to': self.approver_id.email,
                        'attachment_ids': [(6, 0, attachment_ids)] if attachment_ids else False
                    }
                )

            if not template:
                _logger.warning(f'Email template not found for order {self.reference}')
                return


            _logger.info(f'Email sent to {self.approver_id.email} for order {self.reference}')

        except Exception as e:
            _logger.error(f'Email failed for order {self.reference}: {str(e)}')

            self.message_post(
                body=f"Failed to send approval email: {str(e)}",
                message_type='notification'
            )

    def get_approval_url(self):
        try:

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default=False)
            if base_url.startswith('http://'):
                base_url = base_url.replace('http://', 'https://', 1)
            return f"{base_url}/web#model=ord.main&id={self.id}&view_type=form"

        except Exception as e:
            _logger.warning(f"Failed to generate approval URL: {e}")
            # Use your actual domain instead of placeholder
            return f"https://act12-debiandev.autocontrole.be/web#model=ord.main&id={self.id}&view_type=form"

    def write(self, vals):
        result = super().write(vals)

        if 'status' in vals and vals['status'] in ['refused', 'accepted']:
            for record in self:
                record._send_status_notification(vals['status'])

        return result

    def _send_status_notification(self, new_status):
        self.ensure_one()

        if not self.owner_id or not self.owner_id.email:
            _logger.warning(f'No owner or owner email for order {self.reference}')
            return

        try:
            template_ref = f'order.mail_template_order_{new_status}'
            template = self.env.ref(template_ref, raise_if_not_found=False)

            if template:
                template.send_mail(self.id, force_send=True)
                _logger.info(f'Status notification sent for order {self.reference} to {self.owner_id.email}')

        except Exception as e:
            _logger.error(f'Failed to send status notification for order {self.reference}: {str(e)}')

    ui_readonly_state = fields.Selection([
        ('editable', 'Editable'),
        ('readonly', 'Readonly')
    ], compute='_compute_ui_readonly_state')


    def _compute_ui_readonly_state(self):
        """Compute if current user can edit the status field"""
        current_user = self.env.user
        is_approver_ldap = any(group.name == 'odoo_order_approver' for group in current_user.groups_id)

        for record in self:
            has_id = bool(record.id)

            result = has_id and is_approver_ldap

            if result:
                self.ui_readonly_state = 'editable'
            else:
                self.ui_readonly_state = 'readonly'

    @api.model
    def _get_default_department(self):
        """Set default to user's department, but allow selection of others"""
        user_departments = self.env.user.department_ids
        if user_departments:
            return user_departments[0].id
        return False