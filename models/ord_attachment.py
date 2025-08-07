from odoo import models, fields, api, _
from odoo.exceptions import UserError

import base64

class OrdAttachment(models.Model):
    _name = 'ord.attachment'
    _description = 'Order attachment'
    _rec_name = 'filename'

    filename = fields.Char(string='Filename', required=True, default='none')
    extension = fields.Char(string='Extension', store=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    file = fields.Binary(string='File', attachment=True, required=True)
    order_id = fields.Many2one('ord.main', string='Order', required=True)
    size_mb = fields.Float(string='Size (MB)', compute='_compute_file_size', store=True, digits=(10, 2))
    full_filename = fields.Char(string='Full Filename', compute='_compute_full_filename', store=True)

    max_size_mb = 50


    @api.depends('file')
    def _compute_file_size(self):

        for record in self:

            if record.file:

                file_size_bytes = len(base64.b64decode(record.file))
                record.size_mb = file_size_bytes / (1024 * 1024)

                if record.size_mb > record.max_size_mb:
                    raise UserError(
                        _('File size cannot exceed %d MB. Current size: %.2f MB')
                        % (record.max_size_mb, record.size_mb)
                    )
            else:
                record.size_mb = 0

    @api.constrains('file')
    def _check_file_size(self):
        for record in self:
            if record.file:
                file_size_bytes = len(base64.b64decode(record.file))
                record.size_mb = file_size_bytes / (1024 * 1024)
                if record.size_mb > record.max_size_mb:
                    raise UserError(
                        _('File size cannot exceed %d MB. Current size: %.2f MB')
                        % (record.max_size_mb, record.size_mb)
                    )

    @api.constrains('extension')
    def _check_allowed_extensions(self):
        allowed_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
            'txt', 'csv', 'zip', 'rar'
        ]

        for record in self:

                ext_lower = record.extension.lower()
                if ext_lower not in allowed_extensions:
                    raise UserError(
                        _('File extension "%s" is not allowed. Allowed extensions: %s')
                        % (record.extension, ', '.join(allowed_extensions))
                    )

    @api.depends('filename', 'extension')
    def _compute_full_filename(self):
        for record in self:
            if record.filename and record.extension:
                if not record.filename.endswith('.' + record.extension):
                    record.full_filename = f"{record.filename}.{record.extension}"
                else:
                    record.full_filename = record.filename
            elif record.filename:
                record.full_filename = record.filename
            else:
                record.full_filename = "Untitled"

    @api.onchange('filename')
    def _onchange_filename(self):
        if self.filename and '.' in self.filename:
            self.extension = self.filename.split('.')[-1].lower()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'filename' in vals and vals['filename'] and not vals.get('extension'):
                if '.' in vals['filename']:
                    vals['extension'] = vals['filename'].split('.')[-1].lower()
        return super().create(vals_list)

    def action_download(self):
        self.ensure_one()
        if not self.file:
            raise UserError(_('No file to download'))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file/{self.full_filename}?download=true',
            'target': 'self',
        }