from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OrdMainLeg(models.Model):
    _name = 'ord.main.leg'
    _description = 'Legacy order main'
    _rec_name = 'reference'

    # Primary key from legacy system
    legacy_id = fields.Integer(string='Legacy ID', index=True, required=True)

    # Core order information
    sequence = fields.Integer(string='Sequence', required=True)
    order_year = fields.Integer(string='Order Year', required=True)
    reference = fields.Char(string='Reference', size=50, required=True, index=True)
    order_type = fields.Integer(string='Order Type')
    order_date = fields.Datetime(string='Order Date', required=True)

    # People/Relations (stored as integers from legacy system)
    order_owner_id = fields.Integer(string='Order Owner ID', required=True)
    order_destination_id = fields.Integer(string='Order Destination ID', required=True)
    order_approver_id = fields.Integer(string='Order Approver ID')
    supplier_id = fields.Integer(string='Supplier ID', required=True)

    # Content
    subject = fields.Char(string='Subject', size=255, required=True)
    description = fields.Text(string='Description')
    remarks = fields.Text(string='Remarks')

    # Delivery information
    delivery_place = fields.Integer(string='Delivery Place')
    delivery_date = fields.Datetime(string='Delivery Date')
    delivery_remarks = fields.Char(string='Delivery Remarks', size=255)

    # Facturation information
    facturation_date = fields.Datetime(string='Facturation Date')
    facturation_price = fields.Float(string='Facturation Price', digits=(12, 2))
    facturation_remarks = fields.Char(string='Facturation Remarks', size=255)

    # Status and metadata
    status_id = fields.Integer(string='Status ID', required=True)
    date_added = fields.Datetime(string='Date Added')
    order_prevention_type = fields.Integer(string='Order Prevention Type')

    # Computed fields for better readability
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)