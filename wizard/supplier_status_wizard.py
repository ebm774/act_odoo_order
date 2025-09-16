from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SupplierStatusWizard(models.TransientModel):
    _name = 'ord.supplier.status.wizard'
    _description = 'Edit Supplier Status Wizard'

    supplier_id = fields.Many2one('ord.supplier', string='Supplier', required=True, readonly=True)
    status_id = fields.Many2one('ord.supplier.status', string='Status Record', required=True, readonly=True)

    manual_status_override = fields.Boolean(string='Manual Override', default=False)
    status = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('partially-approved', 'Partially-Approved'),
        ('non-approved', 'Non-Approved'),
    ],
        string='Status',
        compute='_compute_status',
        store=False,
    )

    manual_status = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('partially-approved', 'Partially-Approved'),
        ('non-approved', 'Non-Approved'),
    ], string='Manual Status', store=True)

    price = fields.Boolean(string='Price')
    delivery = fields.Boolean(string='Delivery')
    after_sale = fields.Boolean(string='After Sale')
    bill = fields.Boolean(string='Bill')

    status_reason = fields.Text(string='Reason for Change', required=True)

    @api.depends('price', 'delivery', 'after_sale','bill','manual_status_override', 'manual_status')
    def _compute_status(self):

        for record in self:
            if record.manual_status_override:
                if record.manual_status:
                    record.status = record.manual_status
                else:
                    record.status = record.status_id.status if record.status_id else 'new'
                continue
            if record.price and record.delivery and record.after_sale and record.bill:
                record.status = 'approved'
            elif record.price == False and record.delivery == False and record.after_sale == False and record.bill == False:
                record.status = 'non-approved'
            else:
                record.status = 'partially-approved'

    @api.onchange('status')
    def _onchange_status_store_manual(self):
        """Store manually selected status"""
        if self.manual_status_override:
            self.manual_status = self.status

    @api.onchange('manual_status_override')
    def _onchange_manual_override(self):
        """Clear manual status when override is disabled"""
        if not self.manual_status_override:
            self.manual_status = False


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
                    'price' : supplier.status_id.price,
                    'delivery': supplier.status_id.delivery,
                    'after_sale': supplier.status_id.after_sale,
                    'bill': supplier.status_id.bill,
                    'status': supplier.status_id.status,
                })

        return res

    def action_save_changes(self):
        self.ensure_one()

        if not self.status_reason:
            raise UserError(_('Please provide a reason for the changes'))

        reason = self.status_reason

        self.status_id.with_context(change_reason=reason).write({
            'price': self.price,
            'delivery': self.delivery,
            'after_sale': self.after_sale,
            'bill': self.bill,
            'status': self.status,
        })

        return {'type': 'ir.actions.act_window_close'}