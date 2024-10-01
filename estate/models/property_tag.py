from odoo import _,models, fields, api
from odoo.exceptions import UserError

class estate_property_tag(models.Model):
    _name = "estate.property.tag"
    _description="Estate Tag"

    name = fields.Char(required=True)

    _sql_constraints = [
        ("unique_name","UNIQUE(name)","Tag name should be unique")
    ]

