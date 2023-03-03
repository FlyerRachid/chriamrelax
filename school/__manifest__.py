# -*- coding: utf-8 -*-
{
    'name': "Chriamrelax",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': [ 'base_setup',
        'mail',
        'utm',
        'rating',
        'portal',
        'digest','contacts','sale',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/residence.xml',
        'views/templates.xml',
        'data/mail_template_data.xml',
        'data/product.xml',
        'data/ir_sequence_data.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
        'assets': {
        'web.assets_frontend': [
            'school/static/src/js/createDefine.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
