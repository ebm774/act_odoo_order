from odoo import models, fields, api, _
from odoo.exceptions import UserError

import fields


class OrdDestination(models.Model):
    _name = 'ord.destination'
    _description = 'Order destination'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
