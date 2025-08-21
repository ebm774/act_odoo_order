# -*- coding: utf-8 -*-
{
    'name': "Order",

    'summary': "Manage orders of material internally",

    'description': """
        Manage orders of material internally
        =======================================
        
        This module provides tools for the employes to request from direction
        to order new matierials or services to renew the stocks or call a consultant.
        
        Features:
        - Form to request the autorization
        - Adding quote pdf or jpeg or other
        - Mail notification to the selected approver and requester
        - Connection to facturavi
    """,

    'author': "Pierre Dramaix",
    'website': "https://www.autocontrole.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail', 'base_act'],

    # always loaded
    # always respect the loading order
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence.xml',
        'data/users_groups.xml',
        'data/department.xml',
        'data/supplier.xml',
        'data/mail_templates.xml',
        'data/order_main.xml',



        # Views
        'views/ord_main_views.xml',
        'views/ord_sup_views.xml',
        'views/ord_dep_views.xml',
        'views/ord_main_leg_views.xml',
        'views/menu_views.xml',

        # Wizards
        'wizard/supplier_status_wizard_views.xml',

        # Menu views

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

