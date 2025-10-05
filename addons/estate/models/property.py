from odoo import api, fields, models
from odoo.exceptions import ValidationError

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "state desc, expected_price desc, id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)

    currency_id = fields.Many2one("res.currency", required=True, default=lambda self: self.env.company.currency_id.id)
    expected_price = fields.Monetary(required=True, currency_field="currency_id")
    selling_price = fields.Monetary(readonly=True, copy=False, currency_field="currency_id")

    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")
    ])

    property_type_id = fields.Many2one("estate.property.type", string="Type")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    offers_count = fields.Integer(compute="_compute_offer_stats", store=True)
    best_price = fields.Monetary(compute="_compute_offer_stats", currency_field="currency_id", store=True)

    state = fields.Selection([
        ("new", "New"),
        ("offer_received", "Offer Received"),
        ("offer_accepted", "Offer Accepted"),
        ("sold", "Sold"),
        ("canceled", "Canceled"),
    ], default="new", required=True, index=True)

    @api.depends("offer_ids.price", "offer_ids.status")
    def _compute_offer_stats(self):
        for rec in self:
            prices = rec.offer_ids.filtered(lambda o: o.status != "refused").mapped("price")
            rec.offers_count = len(rec.offer_ids)
            rec.best_price = max(prices) if prices else 0.0

    def action_mark_sold(self):
        for rec in self:
            if rec.state == "canceled":
                raise ValidationError("Canceled properties cannot be sold.")
            if rec.best_price and not rec.selling_price:
                rec.selling_price = rec.best_price
            rec.state = "sold"
        return True

    def action_mark_canceled(self):
        for rec in self:
            if rec.state == "sold":
                raise ValidationError("Sold properties cannot be canceled.")
            rec.state = "canceled"
        return True

    def action_open_offers(self):
        self.ensure_one()
        return {
            "name": "Offers",
            "type": "ir.actions.act_window",
            "res_model": "estate.property.offer",
            "domain": [("property_id", "=", self.id)],
            "view_mode": "list,form",
            "target": "current",
        }

    def action_open_best_offer(self):
        self.ensure_one()
        offer = self.offer_ids.sorted(key=lambda o: o.price, reverse=True)[:1]
        if not offer:
            return self.action_open_offers()
        return {
            "name": "Best Offer",
            "type": "ir.actions.act_window",
            "res_model": "estate.property.offer",
            "view_mode": "form",
            "res_id": offer.id,
            "target": "current",
        }
