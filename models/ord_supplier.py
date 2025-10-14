from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OrdSupplier(models.Model):
    _name = 'ord.supplier'
    _description = 'Order supplier'
    _rec_name = 'name'

    legacy_id = fields.Integer(string="Legacy ID")
    name = fields.Char(string="Name", required=True)
    street = fields.Char(string="Street")
    number = fields.Char(string="Number")
    postal_code = fields.Char(string="Postal Code")
    city = fields.Char(string="City")
    phone = fields.Char(string="Phone")
    fax = fields.Char(string="Fax")
    mail = fields.Char(string="Email")
    contact_name = fields.Char(string="Contact name")
    customer_number = fields.Char(string="Customer number")
    status_id = fields.One2many('ord.supplier.status', 'supplier_id', string='Status')

    leg_price = fields.Integer(string='legacy Price')
    leg_delivery = fields.Integer(string='legacy Delivery')
    leg_customerService = fields.Integer(string='legacy CustomerService')


    order_ids = fields.One2many('ord.main', 'supplier_id', string='Orders')
    order_count = fields.Integer(string='Order Count', compute='_compute_order_count', store=True)
    status_log_ids = fields.One2many('ord.supplier.status.log', 'supplier_id', string='Status logs')
    VAT = fields.Char(string='VAT')

    current_status = fields.Selection(
        related='status_id.status',
        string='Current Status',
        store=True,
        readonly=True,
    )



    @api.depends('order_ids')
    def _compute_order_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    def create(self, vals_list):
        suppliers = super().create(vals_list)

        for supplier in suppliers:
            status_vals = {
                'supplier_id': supplier.id,
            }

            if supplier.legacy_id:
                if supplier.leg_price == 1:
                    status_vals['price'] = True
                    status_vals['status'] = 'partially-approved'
                if supplier.leg_delivery == 1:
                    status_vals['delivery'] = True
                    status_vals['status'] = 'partially-approved'
                if supplier.leg_customerService == 1:
                    status_vals['after_sale'] = True
                    status_vals['status'] = 'partially-approved'
                if supplier.leg_price == 1 and supplier.leg_delivery == 1 and supplier.leg_customerService == 1:
                    status_vals['bill'] = True
                    status_vals['status'] = 'approved'
                if supplier.leg_price == 0 and supplier.leg_delivery == 0 and supplier.leg_customerService == 0:
                    status_vals['bill'] = False
                    status_vals['status'] = 'non-approved'


            self.env['ord.supplier.status'].create(status_vals)


        return suppliers

    def action_open_status_wizard(self):
        self.ensure_one()

        if not self.status_id:
            raise UserError(_('No status record found for this supplier'))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Supplier Status',
            'res_model': 'ord.supplier.status.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_supplier_id': self.id,
                'default_status_id': self.status_id.id,
            }
        }

    can_edit_supplier_status = fields.Boolean(
        string='Can Edit Status',
        compute='_compute_can_edit_supplier_status'
    )

    @api.depends_context('uid')
    def _compute_can_edit_supplier_status(self):
        """Check if current user can edit supplier status"""

        param = self.env['ir.config_parameter'].sudo()
        direction_dept_name = param.get_param('order.direction_department_name', 'direction')
        prevention_group_name = param.get_param('order.prevention_group_name', 'odoo_order_prevention')

        for record in self:
            user = self.env.user

            is_direction = False

            if user.department_ids:
                direction_dept = user.department_ids.filtered(lambda d: d.name == direction_dept_name.lower())
                is_direction = bool(direction_dept)

            is_prevention = False
            prevention_group = self.env['res.groups'].search([
                ('name', '=', prevention_group_name)
            ], limit=1)
            if prevention_group and prevention_group in user.groups_id:
                is_prevention = True

            record.can_edit_supplier_status = is_direction or is_prevention





