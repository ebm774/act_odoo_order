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
        readonly=True,
    )


    @api.depends('leg_price', 'leg_delivery', 'leg_customerService')
    def _compute_legacy_fields(self):

        _logger.info("Legacy fields computed")

        for record in self:
            if record.status_id:
                if record.leg_price == 1:
                    record.status_id.price = True
                if record.leg_delivery == 1:
                    record.status_id.delivery = True
                if record.leg_customerService == 1:
                    record.status_id.after_sale = True

    @api.depends('order_ids')
    def _compute_order_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    def create(self, vals_list):
        suppliers = super().create(vals_list)

        for supplier in suppliers:

            self.env['ord.supplier.status'].create({
                'supplier_id': supplier.id,

            })

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