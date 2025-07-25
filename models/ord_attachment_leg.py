from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OrdAttachmentLeg(models.Model):
    _name = 'ord.attachment.leg'
    _description = 'Legacy Order Attachments'
    _rec_name = 'title'


    # SQL: Title (nvarchar(255)) → Odoo: Char
    title = fields.Char(string='Title', size=255, required=True)

    # SQL: Id (int, PK) → Odoo: Integer (with index for performance)
    legacy_id = fields.Integer(string='Legacy ID', index=True)

    # SQL: OrderId (int) → Odoo: Integer
    order_id = fields.Integer(string='Order ID')

    # SQL: OwnerId (int) → Odoo: Integer
    owner_id = fields.Integer(string='Owner ID')

    # SQL: Path (nvarchar(255)) → Odoo: Char
    path = fields.Char(string='Path', size=255)

    # SQL: FileName (nvarchar(255)) → Odoo: Char
    filename = fields.Char(string='File Name', size=255, required=True)

    # SQL: FileSize (int) → Odoo: Integer
    file_size = fields.Integer(string='File Size (bytes)')

    # SQL: FileExtension (nvarchar(50)) → Odoo: Char
    file_extension = fields.Char(string='File Extension', size=50)

    # SQL: Attachment (image) → Odoo: Binary
    attachment_data = fields.Binary(string='Attachment Data')

    # SQL: Source (nvarchar(50)) → Odoo: Char
    source = fields.Char(string='Source', size=50)

    # SQL: DateAdded (datetime) → Odoo: Datetime
    date_added = fields.Datetime(string='Date Added', default=fields.Datetime.now)