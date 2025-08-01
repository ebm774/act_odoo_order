from odoo import models, fields, api, _
from odoo.exceptions import UserError

import base64

class OrdAttachment(models.Model):
    _name = 'ord.attachment'
    _description = 'Order attachment'
    _rec_name = 'filename'

    filename = fields.Char(string='Filename', required=True, default='none')
    size_kb = fields.Float(string='Size', required=True, digit=(10,2))
    extension = fields.Char(string='Extension', compute='_compute_extension', store=True, required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    file = fields.Binary(string='File', attachment=True, required=True)

    order_id = fields.Many2one('ord.main', string='Order', required=True)



    @api.constrains('size_kb')
    def _check_file_size(self):
        max_size_kb = 50 * 1024
        for record in self:
            if record.size_kb > max_size_kb:
                raise UserError(
                    _('File size cannot exceed 50MB. Current size: %.2f MB')
                    % (record.size_kb / 1024)
                )

    @api.constrains('extension')
    def _check_allowed_extensions(self):
        allowed_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
            'txt', 'csv', 'zip', 'rar'
        ]

        for record in self:
            if record.extension and record.extension not in allowed_extensions:
                raise UserError(
                    _('File extension "%s" is not allowed. Allowed extensions: %s')
                    % (record.extension, ', '.join(allowed_extensions))
                )
