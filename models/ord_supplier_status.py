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
    ],string = 'Supplier status', required=True, default='new', store=True)

    price = fields.Boolean(string='Price', default=False)
    delivery = fields.Boolean(string='Delivery', default=False)
    after_sale = fields.Boolean(string='After sale', default=False)
    bill = fields.Boolean(string='Bill', default=False)

    supplier_id = fields.Many2one('ord.supplier', string='Supplier', required=True, ondelete='cascade')

    status_reason = fields.Text(string='Reason')
    change_made = fields.Text(string='Change made')


    change_log_ids = fields.One2many('ord.supplier.status.log', 'status_id', string='Change History')

    _sql_constraints = [
        ('unique_supplier', 'UNIQUE(supplier_id)',
         'Each supplier can only have one status record!'),
    ]

    @api.onchange('price', 'delivery', 'after_sale','bill')
    def _compute_status(self):
        for record in self:
            if record.price and record.delivery and record.after_sale and record.bill:
                record.status = 'approved'
            else:
                record.status = 'non-approved'

    def write(self, vals):

        if ((vals.get('price') and not self.price) or
                (vals.get('delivery') and not self.delivery) or
                (vals.get('after_sale') and not self.after_sale) or
                (vals.get('bill') and not self.bill)):

            if self.env.user not in self.validated_by:
                vals['validated_by'] = [(4, self.env.user.id)]

        return super().write(vals)




