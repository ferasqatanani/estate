from odoo import api, fields, models
from odoo.exceptions import ValidationError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", required=True, string="Buyer")

    currency_id = fields.Many2one(related="property_id.currency_id", readonly=True, store=True)
    price = fields.Monetary(currency_field="currency_id", required=True)

    validity = fields.Integer(default=7)
    status = fields.Selection([
        ("new", "New"),
        ("accepted", "Accepted"),
        ("refused", "Refused"),
    ], default="new", required=True)

    def action_accept(self):
        for rec in self:
            if rec.property_id.state == "sold":
                raise ValidationError("This property is already sold.")
            rec.status = "accepted"
            rec.property_id.state = "offer_accepted"
            rec.property_id.selling_price = rec.price
            # refuse other offers
            others = rec.property_id.offer_ids - rec
            others.filtered(lambda o: o.status == "new").write({"status": "refused"})
        return True

    def action_refuse(self):
        self.filtered(lambda r: r.status == "new").write({"status": "refused"})
        # If all are refused, bounce property back to 'new' unless already sold
        for rec in self.mapped("property_id"):
            if all(o.status == "refused" for o in rec.offer_ids) and rec.state not in ("sold", "canceled"):
                rec.state = "new"
        return True
