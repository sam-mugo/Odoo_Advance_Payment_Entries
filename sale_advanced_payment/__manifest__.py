{
    'name': 'Sale Advance Payment Entry',
    'version': '1.0.0',
    'summary': 'Create draft advance accounting entries from sales orders',
    'category': 'Sales/Accounting',
    'author': 'Assistant',
    'license': 'OPL-1',
    'depends': ['sale','sale_management', 'account'],
    'data': [
        'data/account_data.xml',
        'views/sale_order_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}