# Odoo Estate (Odoo 18)

Tutorial-based **Estate** module for Odoo 18: core models, views, security, and a QWeb HTML report (“Print Property”).

## Features
- Models: `estate.property`, `estate.property.offer`, `estate.property.type`
- State flow: `new → offer_received / offer_accepted → sold / canceled`
- Inline offers with **Accept/Refuse**
- Computed stats (**offers_count**, **best_price**) + stat buttons
- Users form inheritance: **Properties** tab
- QWeb report + **Print Property** button

## Run (local dev)
```bash
cd /home/feras/odoo && source venv/bin/activate
./odoo-bin -c /home/feras/.odoorc \
  --addons-path=/home/feras/odoo/odoo/addons,/home/feras/odoo/addons,/home/feras/projects/odoo-estate/addons \
  -d odoo18 -u estate
