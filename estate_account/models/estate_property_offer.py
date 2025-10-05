from odoo import models


class EstatePropertyOffer(models.Model):
    _inherit = "estate.property.offer"

    def action_accept(self):
        res = super().action_accept()
        for rec in self:
            if rec.status == 'accepted' and rec.property_id:
                # record the buyer on the property
                rec.property_id.buyer_id = rec.partner_id.id
        return res
