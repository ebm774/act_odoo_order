from odoo import models, fields, api, _
from odoo.exceptions import UserError

import base64
import logging
_logger = logging.getLogger(__name__)

class OrdAttachment(models.Model):
    _name = 'ord.attachment'
    _inherit = 'ir.attachment'
    _description = 'Order attachment'

    order_id = fields.Many2one('ord.main', string='Order', required=True)
    full_filename = fields.Char(string='Full Filename', compute='_compute_full_filename', store=True)

    # Override inherited
    name = fields.Char(string='Filename', required=True, default='none')

    max_size_mb = 50
    size_mb = fields.Float(string='Size (MB)', compute='_compute_size_mb', store=True)

    @api.depends('file_size')
    def _compute_size_mb(self):
        for record in self:
            record.size_mb = (record.file_size or 0) / (1024 * 1024)

    @api.constrains('file_size')
    def _check_file_size(self):
        for record in self:
            size_mb  = (record.file_size or 0) / (1024 * 1024)
            if size_mb > record.max_size_mb:
                raise UserError(
                    _('File size cannot exceed %d MB. Current size: %.2f MB')
                    % (record.max_size_mb, size_mb)
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

        _logger.info("#####################################")
        _logger.info("_onchange_datas")
        _logger.info("#####################################")

        if self.datas:
            if not self.name or self.name == 'none':
                self.name = f"attachment_{fields.Datetime.now().strftime('%Y%m%d_%H%M%S')}"


