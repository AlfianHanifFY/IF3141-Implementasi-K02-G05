{
    'name': 'Prospek Klien',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manajemen prospek klien',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/client_prospect_views.xml',
        'views/log_am_views.xml',
    ],
    'application': True,
    'installable': True,
}
