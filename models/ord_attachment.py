from odoo import models, fields, api, _
from odoo.exceptions import UserError

import mimetypes
import base64

import logging
_logger = logging.getLogger(__name__)



class OrdAttachment(models.Model):
    _name = 'ord.attachment'
    _inherit = 'ir.attachment'
    _description = 'Order attachment'

    order_id = fields.Many2one('ord.main', string='Order', required=True)
    full_filename = fields.Char(string='Full Filename', store=True)
    size_mb = fields.Float(string='Size (MB)', store=True, digits=(10, 2))

    # Override inherited
    name = fields.Char(string='Filename', required=True, default='none')
    datas = fields.Binary(string='File', attachment=True)





    @api.constrains('size_mb')
    def _check_file_size(self):
        for record in self:
            if record.size_mb > 50:
                raise UserError(
                    _('File size cannot exceed %d MB. Current size: %.2f MB')
                    % (50, record.size_mb)
                )

    @api.constrains('mimetype')
    def _check_allowed_file_types(self):
        allowed_types = [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg', 'image/png', 'image/gif',
            'text/plain', 'text/csv', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ##docx
        ]

        for record in self:
            if record.mimetype and record.mimetype not in allowed_types:
                raise UserError(
                    _('File type "%s" is not allowed') % record.mimetype
                )

    def action_download(self):

        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        download_url = f"{base_url}/web/content/ord.attachment/{self.id}/datas"

        if self.name:
            download_url += f"/{self.name}"
        download_url += "?download=true"

        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'self',
        }

    def action_preview(self):

        self.ensure_one()
        if not self.datas:
            raise UserError(_('No file to preview'))

        previewable = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'text/plain']

        if self.mimetype in previewable:

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            preview_url = f"{base_url}/web/content/ord.attachment/{self.id}/datas"

            if self.name:
                preview_url += f"/{self.name}"


            return {
                'type': 'ir.actions.act_url',
                'url': preview_url,
                'target': 'new',
            }
        else:

            return self.action_download()

    @api.onchange('datas')
    def _onchange_datas(self):
        if self.datas:
            self.full_filename = getattr(self, 'display_name')
            self.name = getattr(self, 'display_name').rsplit(' ', 1)[0]

            decoded_data = base64.b64decode(self.datas)
            self.size_mb = len(decoded_data) / (1024 * 1024)
            self.mimetype = self._detect_mimetype_from_content(decoded_data, self.name)


    def _detect_mimetype_from_content(self, file_data, filename):
        if not file_data:
            return 'application/octet-stream'

        if file_data.startswith(b'%PDF'):
            return 'application/pdf'
        elif file_data.startswith(b'\xFF\xD8\xFF'):
            return 'image/jpeg'
        elif file_data.startswith(b'\x89PNG'):
            return 'image/png'
        elif file_data.startswith(b'GIF8'):
            return 'image/gif'
        elif file_data.startswith(b'PK\x03\x04'):

            if filename.lower().endswith('.docx'):
                return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.lower().endswith('.xlsx'):
                return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                return 'application/zip'
        elif file_data.startswith(b'\xD0\xCF\x11\xE0'):
            if filename.lower().endswith('.doc'):
                return 'application/msword'
            elif filename.lower().endswith('.xls'):
                return 'application/vnd.ms-excel'
            else:
                return 'application/vnd.ms-office'
        else:
            import mimetypes
            mimetype, _ = mimetypes.guess_type(filename)
            return mimetype or 'application/octet-stream'


