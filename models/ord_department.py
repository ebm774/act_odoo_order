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

    user_ids = fields.Many2many('res.users', string='Department Users')
    user_count = fields.Integer(string='User Count', compute='_compute_user_count', store=True)

    @api.depends('user_ids')
    def _compute_user_count(self):
        for record in self:
            record.user_count = len(record.user_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('viewer_group_id') and vals.get('name'):
                group_vals = {
                    'name': f"Viewer {vals['name']}",  # e.g., "Viewer Marketing"
                    'category_id': self.env.ref('base.module_category_administration').id,
                    'implied_ids': [(4, self.env.ref('order.group_order_user').id)],
                    'comment': f'Auto-created viewer group for department: {vals["name"]}'
                }
                group = self.env['res.groups'].create(group_vals)
                vals['viewer_group_id'] = group.id

        records = super().create(vals_list)

        for record in records:
            if record.viewer_group_id and record.user_ids:
                record._update_viewer_group_users()

        return records


    def write(self, vals):
        result = super().write(vals)

        if 'user_ids' in vals and self.viewer_group_id:
            self._update_viewer_group_users()

        return result

    def _update_viewer_group_users(self):
        for record in self:
            if record.viewer_group_id:
                record.viewer_group_id.write({
                    'users': [(6, 0, record.user_ids.ids)] #NB : replace all users
                })

