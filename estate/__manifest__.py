{
  'name': 'Estate',
  'version': '12.0',
  'summary': 'Tutorial Day 10–12 (Odoo 18 compatible)',
  'license': 'LGPL-3',
  'depends': ['base'],
  'data': [
    'security/ir.model.access.csv',
    'views/estate_property_type_views.xml',
    'views/estate_offer_views.xml',
    'views/estate_property_views.xml',
    'views/res_users_views.xml',   # <-- Day 12 addition
    'views/estate_menus.xml',
  'views/report_estate_property.xml',        # <— Day 14
    'views/estate_property_report_button.xml', # <— Day 14
],
  'application': True,
}
