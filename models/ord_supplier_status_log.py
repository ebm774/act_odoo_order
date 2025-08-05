from odoo import models, fields, api, _


class OrdSupplierStatusLog(models.Model):
    _name = 'ord.supplier.status.log'
    _description = 'Supplier Status Change Log'
    _order = 'change_date desc'
    _rec_name = 'changes'

    status_id = fields.Many2one('ord.supplier.status', string='Status', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Changed By', required=True, default=lambda self: self.env.user)
    change_date = fields.Datetime(string='Change Date', required=True, default=fields.Datetime.now)
    changes = fields.Char(string='Changes Made', required=True)
    reason = fields.Text(string='Reason', required=True)