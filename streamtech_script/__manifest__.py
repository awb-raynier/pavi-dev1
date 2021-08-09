# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Streamtech Data Migration Scripts",

    'summary': """
        Streamtech Data Migration Scripts
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Data Migration',

    'version': '13.0.0.0.1',

    'depends': [
        'base',
        'mail'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/streamtech_scripts_view.xml',
        'views/menuitem.xml',
        'data/streamtech_scripts_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
