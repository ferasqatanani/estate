from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EstateProperty(models.Model):
    _inherit = "estate.property"

    # Buyer of the property (filled when an offer is accepted)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    # Link to created customer invoice
    invoice_id = fields.Many2one("account.move", string="Invoice", copy=False)

    def action_create_invoice(self):
        """Create a customer invoice for this sold property (e.g., commission)."""
        self.ensure_one()
        if self.state != 'sold':
            raise ValidationError("You can create an invoice only when the property is Sold.")
        if not self.buyer_id:
            raise ValidationError("Please set a Buyer (accept an offer) before invoicing.")
        if self.invoice_id:
            # Already created — just open it
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "res_id": self.invoice_id.id,
                "view_mode": "form",
                "target": "current",
            }

        # Example: 6% commission on selling_price
        commission = (self.selling_price or 0.0) * 0.06

        move = self.env['account.move'].create({
            "move_type": "out_invoice",
            "partner_id": self.buyer_id.id,
            "invoice_line_ids": [(0, 0, {
                "name": f"Commission for {self.name}",
                "quantity": 1.0,
                "price_unit": commission,
            })],
        })
        self.invoice_id = move.id

        # Open the invoice form
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_invoice(self):
        """Smart button: open existing invoice."""
        self.ensure_one()
        if not self.invoice_id:
            raise ValidationError("No invoice linked to this property.")
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.invoice_id.id,
            "view_mode": "form",
            "target": "current",
        }
