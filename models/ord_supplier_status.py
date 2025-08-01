from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OrdSupplierStatus(models.Model):
    _name = 'ord.supplier.status'
    _description = 'Order supplier status'
    _rec_name = 'status'

    status = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('non-approved', 'Non-Approved'),
    ],string = 'Supplier status', required=True, default='new', compute='_compute_status', store=True)

    price = fields.Boolean(string='Price')
    delivery = fields.Boolean(string='Delivery')
    after_sale = fields.Boolean(string='After sale')

    supplier_id = fields.One2many('ord.supplier', 'status_id', string='Supplier')

    @api.depends('price', 'delivery', 'after_sale')
    def _compute_status(self):
        for record in self:
            if record.price and record.delivery and record.after_sale:
                record.status = 'approved'
            elif not record.price and not record.delivery and not record.after_sale:
                 record.status = 'new'
            else:
                record.status = 'non-approved'

