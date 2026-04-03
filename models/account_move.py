# -*- coding: utf-8 -*-
 
from odoo import api, fields, models
 
 
class AccountMove(models.Model):
    _inherit = 'account.move'
 
    x_building_pay_partner_name = fields.Char(
        string='Nome intestatario BuildingPay',
        compute='_compute_building_pay_partner_name',
        store=True,
        help='Nome del contatto di fatturazione senza il nome del padre. '
             'Utilizzato nel report della fattura al posto di display_name '
             'che in Odoo concatena "Padre, Figlio".',
    )
 
    @api.depends('partner_id', 'partner_id.name', 'partner_id.parent_id')
    def _compute_building_pay_partner_name(self):
        for move in self:
            partner = move.partner_id
            # partner.name contiene solo il nome del contatto stesso,
            # mentre partner.display_name restituisce "Padre, Figlio".
            # Usiamo partner.name per ottenere solo il nome figlio.
            move.x_building_pay_partner_name = partner.name if partner else False
 
