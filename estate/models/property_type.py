from odoo import _,models, fields, api
from odoo.exceptions import UserError

class estate_property_type(models.Model):
    _name = "estate.property.type"
    _description="Estate Type"

    name = fields.Char(required=True)