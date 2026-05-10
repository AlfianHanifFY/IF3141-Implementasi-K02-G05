{
    'name': 'Monitor',
    'version': '17.0.1.0.0',
    'category': 'Monitoring',
    'summary': 'Monitoring Umum',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['base', 'client_prospect', 'dokumen'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/monitor_target_views.xml',
        'views/monitor_proyek_views.xml',
    ],
    'application': True,
    'installable': True,
}
