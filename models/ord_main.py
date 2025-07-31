from odoo import models, fields, api, _
from odoo.exceptions import UserError

import fields


class OrdMain(models.Model):
    _name = 'ord.main'
    _description = 'Order main'
    _rec_name = 'reference'


    reference = fields.Char(string='Reference', size=50)
    creation_date = fields.Datetime(string='Creation date', required=True, default=fields.Datetime.now)
    owner_id = fields.Many2one('res.users', string='Owner', required=True, ondelete='cascade')
    destination_id = fields.Many2one('ord.destination', string='Destination', required=True)
    approver_id = fields.Many2one('res.users', string='Approver', required=True)

    ticket_id = fields.Many2one('ord.ticket', string='Ticket', required=True)
    _sql_constraints = [
        ('unique_ticket', 'UNIQUE(ticket_id)',
         'Each ticket can only be assigned once!'),
    ]

    supplier_id = fields.Many2one('ord.supplier', string='Supplier', required=True)
    type = fields.Selection([
        ('material', 'Material'),
        ('service', 'Service')
    ], string = 'Order type', required=True, default='material')

    attachment_ids = fields.One2many('ord.attachment', 'order_id', string='Attachments')
    viewer_ids = fields.Many2many('res.groups', string='Viewers')