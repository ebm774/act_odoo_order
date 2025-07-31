from odoo import models, fields, api, _
from odoo.exceptions import UserError

import fields


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
    status_id = fields.Many2one('ord_status', string='Status', required=True)
