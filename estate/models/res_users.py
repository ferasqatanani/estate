from odoo import fields, models

class ResUsers(models.Model):
    _inherit = "res.users"

    # List of properties where this user is the salesperson
    property_ids = fields.One2many(
        "estate.property",
        "salesperson_id",
        string="Properties",
        domain=[("state", "not in", ("sold", "canceled"))],  # only available ones
    )

