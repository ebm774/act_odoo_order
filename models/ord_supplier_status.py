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

    supplier_id = fields.Many2one('ord.supplier', string='Supplier', required=True, ondelete='cascade')
    validation_notes = fields.Text(string='Validation Notes')
    validated_by = fields.Many2many('res.users', string='Validated By', readonly=True)
    validation_date = fields.Datetime(string='Validation Date', readonly=True)

    _sql_constraints = [
        ('unique_supplier', 'UNIQUE(supplier_id)',
         'Each supplier can only have one status record!'),
    ]

    @api.depends('price', 'delivery', 'after_sale')
    def _compute_status(self):
        for record in self:
            if record.price and record.delivery and record.after_sale:
                record.status = 'approved'
                record.validation_date = fields.Datetime.now()
            elif not record.price and not record.delivery and not record.after_sale:
                 record.status = 'new'
            else:
                record.status = 'non-approved'

    def write(self, vals):

        if ((vals.get('price') and not self.price) or
                (vals.get('delivery') and not self.delivery) or
                (vals.get('after_sale') and not self.after_sale)):

            if self.env.user not in self.validated_by:
                vals['validated_by'] = [(4, self.env.user.id)]

        return super().write(vals)




