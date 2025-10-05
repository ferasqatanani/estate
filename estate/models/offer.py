from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc, id desc"

    property_id = fields.Many2one(
        "estate.property", string="Property",
        required=True, ondelete="cascade", index=True
    )
    partner_id = fields.Many2one("res.partner", string="Buyer", required=True)

    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    price = fields.Monetary(required=True, currency_field="currency_id")
    validity = fields.Integer(string="Validity (days)", default=7)

    status = fields.Selection(
        [('new', 'New'), ('accepted', 'Accepted'), ('refused', 'Refused')],
        default='new', required=True, index=True
    )

    @api.constrains('price')
    def _check_price_positive(self):
        for rec in self:
            if rec.price is None or rec.price <= 0:
                raise ValidationError("Offer price must be strictly positive.")

    # --- Day 12: enforce strictly higher than current best; set property state ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            prop_id = vals.get("property_id")
            price = vals.get("price") or 0
            if prop_id:
                best = self.search([("property_id", "=", prop_id)], limit=1, order="price desc")
                if best and price <= best.price:
                    raise ValidationError(
                        "Offer must be strictly higher than the current best offer (%.2f)." % best.price
                    )
        recs = super().create(vals_list)
        for rec in recs:
            if rec.property_id and rec.property_id.state in ('new', 'offer_received'):
                rec.property_id.state = 'offer_received'
        return recs

    # existing accept/refuse from Day 10
    def action_accept(self):
        for rec in self:
            others = rec.property_id.offer_ids.filtered(lambda o: o.id != rec.id and o.status == 'accepted')
            if others:
                raise ValidationError("Another offer is already accepted for this property.")
            rec.status = 'accepted'
            if rec.property_id.state not in ('sold', 'canceled'):
                rec.property_id.state = 'offer_accepted'
        return True

    def action_refuse(self):
        for rec in self:
            rec.status = 'refused'
            if rec.property_id.state == 'offer_accepted':
                remaining = rec.property_id.offer_ids.filtered(lambda o: o.status != 'refused')
                rec.property_id.state = 'offer_received' if remaining else 'new'
        return True

