# -*- coding: utf-8 -*-
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

    order_id = fields.Many2one('ord.main', string='Order', required=True, ondelete='cascade')
    full_filename = fields.Char(string='Full Filename', store=True)
    size_mb = fields.Float(string='Size (MB)', store=True, digits=(10, 2))
    name = fields.Char(string='Filename', required=True)
    datas = fields.Binary(string='File', attachment=True, required=True)

    # ========== Configuration Methods ==========

    def _get_attachment_config(self):
        """
        Get all attachment configuration parameters at once.
        Caches results to avoid repeated database calls.
        Returns dict with: max_size_mb, allowed_extensions, allowed_mimetypes
        """
        param = self.env['ir.config_parameter'].sudo()

        # Get comma-separated strings
        allowed_ext_str = param.get_param('order.attachment_allowed_extensions', 'pdf')
        allowed_mime_str = param.get_param('order.attachment_allowed_mimetypes', 'application/pdf')
        max_size_str = param.get_param('order.attachment_max_size', '10')

        return {
            'max_size_mb': float(max_size_str),
            'allowed_extensions': [ext.strip().lower() for ext in allowed_ext_str.split(',')],
            'allowed_mimetypes': [mime.strip() for mime in allowed_mime_str.split(',')],
            'allowed_extensions_display': allowed_ext_str.upper(),
        }

    # ========== Validation Constraints ==========

    @api.constrains('size_mb')
    def _check_file_size(self):
        """Validate file size against configured maximum"""
        config = self._get_attachment_config()
        max_size = config['max_size_mb']

        for record in self:
            if record.size_mb > max_size:
                raise UserError(
                    _('File size cannot exceed %.0f MB. Current size: %.2f MB')
                    % (max_size, record.size_mb)
                )

    @api.constrains('mimetype')
    def _check_allowed_file_types(self):
        """Validate mimetype against configured allowed types"""
        config = self._get_attachment_config()

        for record in self:
            if record.mimetype and record.mimetype not in config['allowed_mimetypes']:
                raise UserError(
                    _('File type "%s" is not allowed.\n\nOnly these file types are allowed: %s')
                    % (record.mimetype, config['allowed_extensions_display'])
                )

    @api.constrains('name', 'mimetype')
    def _check_extension_matches_mimetype(self):
        """Validate file extension is in allowed list"""
        config = self._get_attachment_config()

        for record in self:
            if not record.name or not record.mimetype or '.' not in record.name:
                continue

            extension = record.name.rsplit('.', 1)[1].lower()

            if extension not in config['allowed_extensions']:
                raise UserError(
                    _('File extension ".%s" is not allowed.\n\nOnly these extensions are allowed: %s')
                    % (extension, config['allowed_extensions_display'])
                )

    @api.constrains('datas', 'name')
    def _check_attachment_has_file(self):
        """Ensure attachment has actual file data and valid filename"""
        for record in self:
            if not record.exists():
                continue

            # Check file has content
            has_file = False
            if record.datas:
                try:
                    decoded = base64.b64decode(record.datas)
                    has_file = len(decoded) > 0
                except:
                    has_file = False

            if not has_file and not record.store_fname:
                raise UserError(
                    _('Cannot save attachment without uploading a file. Please select a file to upload.')
                )

            # Check filename is valid
            if not record.name or not record.name.strip():
                raise UserError(
                    _('Attachment must have a valid filename.')
                )

    # ========== File Processing Methods ==========

    @api.onchange('datas')
    def _onchange_datas(self):
        """Update mimetype, size, and filename when file is selected in UI"""
        if not self.datas:
            if not self.id:  # Only clear if new record
                self.name = False
                self.mimetype = False
                self.size_mb = 0.0
                self.full_filename = False
            return

        try:
            decoded_data = base64.b64decode(self.datas)
            self.size_mb = len(decoded_data) / (1024 * 1024)
            self.mimetype = self._detect_mimetype_from_content(decoded_data, self.name or 'file')

            if self.name:
                self.name = self._ensure_extension(self.name, self.mimetype)
                self.full_filename = self.name

        except Exception as e:
            _logger.warning(f"Error processing attachment data: {e}")
            return

    def _ensure_extension(self, filename, mimetype):
        """Ensure filename has appropriate extension based on mimetype"""
        if not filename or not mimetype:
            return filename

        # Check if already has valid extension
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2 and len(name_parts[1]) <= 8 and name_parts[1].replace('_', '').isalnum():
            return filename

        # Add extension from mimetype
        filename = filename.rstrip('.')
        extension = mimetypes.guess_extension(mimetype)
        if extension:
            extension = extension.lstrip('.').lower()
            return f"{filename}.{extension}"

        return filename

    def _detect_mimetype_from_content(self, file_data, filename):
        """Detect mimetype by reading file binary signature (magic bytes)"""
        if not file_data:
            return 'application/octet-stream'

        # Check binary signatures
        if file_data.startswith(b'%PDF'):
            return 'application/pdf'
        elif file_data.startswith(b'\xFF\xD8\xFF'):
            return 'image/jpeg'
        elif file_data.startswith(b'\x89PNG'):
            return 'image/png'
        elif file_data.startswith(b'GIF8'):
            return 'image/gif'
        elif file_data.startswith(b'PK\x03\x04'):
            # ZIP-based formats (Office files)
            if filename.lower().endswith('.docx'):
                return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.lower().endswith('.xlsx'):
                return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                return 'application/zip'
        elif file_data.startswith(b'\xD0\xCF\x11\xE0'):
            # Old Office formats
            if filename.lower().endswith('.doc'):
                return 'application/msword'
            elif filename.lower().endswith('.xls'):
                return 'application/vnd.ms-excel'
            else:
                return 'application/vnd.ms-office'
        else:
            # Fallback to Python's mimetypes library
            mimetype, _ = mimetypes.guess_type(filename)
            return mimetype or 'application/octet-stream'

    # ========== CRUD Operations ==========


    def _process_file_data(self, vals, existing_name=None):
        """
        Process file data: detect mimetype, calculate size, ensure extension.
        Modifies vals dict in place.

        :param vals: Dictionary of values being created/written
        :param existing_name: Existing filename (for write operations), None for create
        """
        if not vals.get('datas'):
            return

        decoded_data = base64.b64decode(vals['datas'])
        filename = vals.get('name', existing_name or 'file')
        mimetype = self._detect_mimetype_from_content(decoded_data, filename)

        vals['mimetype'] = mimetype
        vals['size_mb'] = len(decoded_data) / (1024 * 1024)
        vals['name'] = self._ensure_extension(filename, mimetype)
        vals['full_filename'] = vals['name']

    @api.model_create_multi
    def create(self, vals_list):
        """Process file data and add extension when creating attachment"""
        for vals in vals_list:
            self._process_file_data(vals)
        return super().create(vals_list)

    def write(self, vals):
        """Process file data and add extension when updating attachment"""
        if 'datas' in vals:
            self._process_file_data(vals, existing_name=self.name)
        return super().write(vals)

    # ========== User Actions ==========

    def action_download(self):
        """Generate download URL for attachment"""
        self.ensure_one()

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url and base_url.startswith('http://'):
            base_url = base_url.replace('http://', 'https://', 1)

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
        """Preview attachment if file type is previewable, otherwise download"""
        self.ensure_one()

        if not self.datas:
            raise UserError(_('No file to preview'))

        previewable = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'text/plain']

        if self.mimetype in previewable:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if base_url and base_url.startswith('http://'):
                base_url = base_url.replace('http://', 'https://', 1)

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