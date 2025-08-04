from odoo import models, fields, api, _
from odoo.exceptions import UserError



class OrdDepartment(models.Model):
    _name = 'ord.department'
    _description = 'Order department'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    order_ids = fields.One2many('ord.main', 'department_id', string='Orders')

    viewer_group_id = fields.Many2one(
        'res.groups',
        string='Viewer Group',
        help='Group that can view orders for this department'
    )

