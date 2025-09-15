from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class OrdSupplierStatus(models.Model):
    _name = 'ord.supplier.status'
    _description = 'Order supplier status'
    _rec_name = 'status'

    status = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('partially-approved', 'Partially-Approved'),
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
            if any([record.price, record.delivery, record.after_sale, record.bill]):
                if not record.status_reason :
                    return {
                        'warning': {
                            'title': _('Required Information Missing'),
                            'message': _(
                                'You must fill "Reason" fields before saving. '
                                'These changes will not be saved without this information.'
                            )
                        }
                    }

            if record.price and record.delivery and record.after_sale and record.bill:
                record.status = 'approved'
            elif record.price == False and record.delivery == False and record.after_sale == False and record.bill == False:
                record.status = 'non-approved'
            else:
                record.status = 'partially-approved'

    def write(self, vals):


        for record in self:
            validation_fields = ['price','delivery','after_sale','bill']
            changed_fields = []

            for field in validation_fields:
                if field in vals and vals[field] != getattr(record, field):
                    field_label = record._fields[field].string
                    old_value = getattr(record, field)
                    new_value = vals[field]
                    changed_fields.append(f"{field_label}: {old_value} → {new_value}")

            if changed_fields:
                reason = self.env.context.get('change_reason') or vals.get('status_reason', record.status_reason)

                if not reason :
                    raise UserError(_(
                        'When changing validation criteria, you must provide '
                        '"Reason" information.'
                    ))

                self.env['ord.supplier.status.log'].create({
                    'status_id': record.id,
                    'changes': ', '.join(changed_fields),
                    'reason': reason,
                    'user_id': self.env.user.id,
                    'change_date': fields.Datetime.now(),
                    'supplier_id': record.supplier_id.id,
                })

                if 'status_reason' in vals:
                    vals['status_reason'] = False
                if 'change_made' in vals:
                    vals['change_made'] = False

        return super().write(vals)




