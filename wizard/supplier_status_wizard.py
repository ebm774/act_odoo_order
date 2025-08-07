from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupplierStatusWizard(models.TransientModel):
    _name = 'supplier.status.wizard'
    _description = 'Edit Supplier Status Wizard'

    supplier_id = fields.Many2one('ord.supplier', string='Supplier', required=True, readonly=True)
    status_id = fields.Many2one('ord.supplier.status', string='Status Record', required=True, readonly=True)

    status = fields.Selection(
        related='status_id.status',
        string='Status',
        readonly=True
    )
    price = fields.Boolean(related='status_id.price', string='Price')
    delivery = fields.Boolean(related='status_id.delivery', string='Delivery')
    after_sale = fields.Boolean(related='status_id.after_sale', string='After Sale')
    bill = fields.Boolean(related='status_id.bill', string='Bill')

    status_reason = fields.Text(string='Reason for Change', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        supplier_id = self.env.context.get('active_id')
        if supplier_id:
            supplier = self.env['ord.supplier'].browse(supplier_id)
            if supplier.status_id:
                res.update({
                    'supplier_id': supplier.id,
                    'status_id': supplier.status_id.id,
                })

        return res

    def action_save_changes(self):
        self.ensure_one()

        if not self.status_reason:
            raise UserError(_('Please provide a reason for the changes'))

        self.status_id.write({
            'price': self.price,
            'delivery': self.delivery,
            'after_sale': self.after_sale,
            'bill': self.bill,
            'status_reason': self.status_reason,
        })

        return {'type': 'ir.actions.act_window_close'}