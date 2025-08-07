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

    current_status = fields.Selection(
        related='status_id.status',
        string='Current Status',
        readonly=True,
    )


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
            'res_model': 'supplier.status.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_supplier_id': self.id,
                'default_status_id': self.status_id.id,
            }
        }