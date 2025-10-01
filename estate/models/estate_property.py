from odoo import fields, models

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property (minimal)"

    name = fields.Char(required=True)
    expected_price = fields.Float()
