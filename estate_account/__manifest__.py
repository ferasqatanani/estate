{
  'name': 'Estate / Accounting Bridge',
  'version': '13.0',
  'summary': 'Day 13: Interact with Accounting (Odoo 18)',
  'license': 'LGPL-3',
  'depends': ['estate', 'account'],  # estate = your app; account = Invoicing
  'data': [
    'views/estate_property_views.xml',
  ],
  'application': False,
}
