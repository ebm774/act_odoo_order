from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class OrdMain(models.Model):
    _name = 'ord.main'
    _description = 'Order main'
    _rec_name = 'reference'

    status = fields.Selection([
        ('waiting', 'Waiting'),
        ('refused', 'Refused'),
        ('accepted', 'Accepted'),
    ], default='waiting', string='Order status')

    reference = fields.Char(
        string='Reference',
        size=50,
        readonly=True,
        default='TBD',
        copy=False,
        )

    creation_date = fields.Datetime(string='Creation date', required=True, default=fields.Datetime.now)
    owner_id = fields.Many2one('res.users', string='Owner', required=True, default=lambda self: self.env.user)
    department_id = fields.Many2one('ord.department', string='Department', required=True)
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        required=True,
        domain=lambda self: [('groups_id', 'in', [self.env.ref('order.group_order_approver').id])],
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
        domain="[('status_id.status', '=', 'approved')]"
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
        help='Groups that can view this order',
        hidden='Yes'
    )

    @api.depends('new_ticket_subject', 'new_ticket_description')
    def _compute_ticket(self):
        for order in self:
            order.new_ticket_subject = order.ticket_id.subject
            order.new_ticket_description = order.ticket_id.description

    @api.depends('department_id', 'department_id.viewer_group_id', 'owner_id')
    def _compute_viewer_ids(self):
        for record in self:
            viewer_groups = self.env['res.groups']

            if record.department_id and record.department_id.viewer_group_id:
                viewer_groups += record.department_id.viewer_group_id

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


        return super().create(vals_list)