from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "state desc, expected_price desc, id desc"

    # --- Core ---
    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(string="Available From")

    # Money
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    expected_price = fields.Monetary(required=True, currency_field="currency_id")
    selling_price = fields.Monetary(readonly=True, copy=False, currency_field="currency_id")

    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"),
                   ("east", "East"), ("west", "West")]
    )

    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled'),
    ], default='new', required=True, index=True)

    # --- Relations ---
    property_type_id = fields.Many2one(
        "estate.property.type", string="Property Type",
        ondelete="set null", index=True
    )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # Day 12: salesperson who owns the property
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson",
        default=lambda self: self.env.user, index=True
    )

    # --- Day 11 stats ---
    offers_count = fields.Integer(string="Offers", compute="_compute_offer_stats", store=False)
    best_price = fields.Monetary(
        string="Best Offer", compute="_compute_offer_stats",
        currency_field="currency_id", store=False
    )

    @api.depends('offer_ids.price', 'offer_ids.status')
    def _compute_offer_stats(self):
        for rec in self:
            valid = rec.offer_ids.filtered(lambda o: o.status != 'refused')
            prices = valid.mapped('price')
            rec.offers_count = len(prices)
            rec.best_price = max(prices) if prices else 0.0

    # --- Day 10 business rules ---
    @api.constrains('expected_price')
    def _check_expected_price_positive(self):
        for rec in self:
            if rec.expected_price is None or rec.expected_price <= 0:
                raise ValidationError("Expected price must be strictly positive.")

    def action_mark_canceled(self):
        for rec in self:
            if rec.state == 'sold':
                raise ValidationError("Sold properties cannot be canceled.")
            rec.state = 'canceled'
        return True

    def action_mark_sold(self):
        for rec in self:
            if rec.state == 'canceled':
                raise ValidationError("Canceled properties cannot be sold.")
            accepted = rec.offer_ids.filtered(lambda o: o.status == 'accepted')
            if len(accepted) != 1:
                raise ValidationError("Exactly one accepted offer is required to sell.")
            rec.selling_price = accepted.price
            rec.state = 'sold'
        return True

    # --- Day 11 helpers (stat buttons) ---
    def action_open_offers(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Offers",
            "res_model": "estate.property.offer",
            "view_mode": "list,form",
            "domain": [("property_id", "=", self.id)],
            "target": "current",
        }

    def action_open_best_offer(self):
        self.ensure_one()
        best = self.offer_ids.sorted(lambda o: o.price, reverse=True)[:1]
        if best:
            return {
                "type": "ir.actions.act_window",
                "res_model": "estate.property.offer",
                "res_id": best.id,
                "view_mode": "form",
                "target": "current",
            }
        return False

    # --- Day 12: forbid deleting unless new/canceled ---
    @api.ondelete(at_uninstall=False)
    def _check_ondelete_state(self):
        bad = self.filtered(lambda r: r.state not in ('new', 'canceled'))
        if bad:
            raise ValidationError("You can only delete properties in states New or Canceled.")
