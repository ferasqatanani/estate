from odoo import api, fields, models

class EstateProperty(models.Model):
    _inherit = "estate.property"

    invoice_count = fields.Integer(
        string="Invoices",
        compute="_compute_invoice_count",
        store=False,
    )

    def _compute_invoice_count(self):
        for prop in self:
            partner = prop.buyer_id
            if not partner:
                prop.invoice_count = 0
                continue
            prop.invoice_count = self.env["account.move"].search_count([
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("partner_id", "=", partner.id),
            ])

    def action_open_invoices(self):
        self.ensure_one()
        partner = self.buyer_id
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        domain = []
        if partner:
            domain = [("move_type", "in", ["out_invoice", "out_refund"]),
                      ("partner_id", "=", partner.id)]
        action["domain"] = domain
        action["context"] = {"default_move_type": "out_invoice", "search_default_customer": 1}
        return action
