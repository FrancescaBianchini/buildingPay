# -*- coding: utf-8 -*-
 
from odoo import fields, models
 
 
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
 
    building_pay_managed = fields.Boolean(
        string='Gestito da BuildingPay',
        default=False,
        help='Indica che questo conto bancario è stato creato '
             'automaticamente dal modulo BuildingPay tramite il campo IBAN.',
    )
 
