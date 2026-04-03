# -*- coding: utf-8 -*-
{
    'name': 'BuildingPay Portal',
    'version': '17.0.1.0.0',
    'category': 'Website/eCommerce',
    'summary': 'Gestione BuildingPay: contratti, IBAN, abilitazione e accordi portale',
    'description': """
BuildingPay Portal
==================
Modulo per Odoo 17 EE che estende il portale clienti con:

* Campi contratto (upload), IBAN e abilitazione sugli indirizzi di fatturazione
* Nuovo gruppo di accesso 'Building Pay Manager'
* Accordo contrattuale obbligatorio nel profilo portale
* Checkout eCommerce filtrato per indirizzi abilitati BuildingPay
* Intestazione fattura con solo il nome del contatto figlio (senza padre)
    """,
    'author': 'Custom',
    'website': '',
    'depends': [
        'portal',
        'website_sale',
        'account',
        'sale',
    ],
    'data': [
        # --- Security (caricato per primo) ---
        'security/building_pay_groups.xml',
        'security/ir.model.access.csv',
        # --- Views backend ---
        'views/res_partner_views.xml',
        # --- Views frontend / portale ---
        'views/portal_templates.xml',
        'views/website_sale_templates.xml',
        # --- Report ---
        'views/report_invoice_building_pay.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'building_pay/static/src/js/portal_building_pay.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
