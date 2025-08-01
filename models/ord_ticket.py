from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OrdTicket(models.Model):
    _name = 'ord.ticket'
    _description = 'Order ticket'
    _rec_name = 'subject'

    subject = fields.Char(string="Subject", required=True)
    description = fields.Char(string="Description", required=False)

    order_ids = fields.One2many('ord.main', 'ticket_id', string='Orders ticket')
