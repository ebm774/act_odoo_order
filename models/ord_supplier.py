from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OrdSupplier(models.Model):
    _name = 'ord.supplier'
    _description = 'Order supplier'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    street = fields.Char(string="Street", required=True)
    number = fields.Char(string="Number", required=True)
    city = fields.Char(string="City", required=True)
    phone = fields.Char(string="Phone", required=True)
    mail = fields.Char(string="Email", required=True)
    contact_name = fields.Char(string="Contact name", required=True)
    status_id = fields.One2many('ord.supplier.status', 'supplier_id', string='Status')
    order_ids = fields.One2many('ord.main', 'supplier_id', string='Orders')
    order_count = fields.Integer(string='Order Count', compute='_compute_order_count', store=True)


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