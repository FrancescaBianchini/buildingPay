# -*- coding: utf-8 -*-

import base64

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # -------------------------------------------------------------------------
    # Campi sull'indirizzo di fatturazione (type='invoice')
    # -------------------------------------------------------------------------

    x_building_pay_contratto = fields.Binary(
        string='Contratto',
        attachment=True,
        help='Documento contratto BuildingPay relativo a questo indirizzo di fatturazione.',
    )
    x_building_pay_contratto_filename = fields.Char(
        string='Nome file contratto',
    )
    x_building_pay_contratto_caricato = fields.Boolean(
        string='Contratto caricato',
        compute='_compute_contratto_caricato',
        store=True,
        readonly=True,
        help='Spuntato automaticamente quando il documento contratto viene caricato.',
    )
    x_building_pay_iban = fields.Char(
        string='IBAN',
        help='Codice IBAN del contatto. '
             'Viene salvato automaticamente nel conto corrente bancario del partner.',
    )
    x_building_pay_abilitato = fields.Boolean(
        string='Abilitato al servizio BuildingPay',
        default=False,
        help='Se attivo, questo indirizzo di fatturazione è abilitato '
             'al servizio BuildingPay. '
             'Modificabile solo dagli utenti con il ruolo Building Pay Manager.',
    )

    # -------------------------------------------------------------------------
    # Campi sul contatto principale (profilo portale)
    # -------------------------------------------------------------------------

    x_building_pay_accordo = fields.Binary(
        string='Accordo contrattuale con Progetti e Soluzioni',
        attachment=True,
        help='Documento di accordo contrattuale obbligatorio per effettuare ordini '
             'tramite il portale.',
    )
    x_building_pay_accordo_filename = fields.Char(
        string='Nome file accordo',
    )

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------

    @api.depends('x_building_pay_contratto')
    def _compute_contratto_caricato(self):
        for partner in self:
            partner.x_building_pay_contratto_caricato = bool(
                partner.x_building_pay_contratto
            )

    # -------------------------------------------------------------------------
    # Override create / write per sincronizzare IBAN → res.partner.bank
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        for partner, vals in zip(partners, vals_list):
            if vals.get('x_building_pay_iban'):
                partner._sync_building_pay_bank_account(vals['x_building_pay_iban'])
        return partners

    def write(self, vals):
        res = super().write(vals)
        if 'x_building_pay_iban' in vals:
            for partner in self:
                partner._sync_building_pay_bank_account(vals['x_building_pay_iban'])
        return res

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _sync_building_pay_bank_account(self, iban):
        """Crea o aggiorna il conto bancario BuildingPay del partner.

        Se l'IBAN è vuoto, non esegue nulla.
        Rimuove eventuali conti precedentemente creati da BuildingPay
        prima di crearne uno nuovo, in modo da mantenere sempre
        un solo conto BuildingPay per partner.
        """
        self.ensure_one()
        if not iban or not iban.strip():
            return

        iban_clean = iban.strip().upper().replace(' ', '')
        BankAccount = self.env['res.partner.bank'].sudo()

        # Controlla se il conto esiste già con lo stesso numero
        existing = BankAccount.search([
            ('partner_id', '=', self.id),
            ('acc_number', '=', iban_clean),
        ], limit=1)

        if existing:
            return  # Nulla da fare, il conto è già presente e corretto

        # Rimuove i conti BuildingPay precedenti per questo partner
        old_accounts = BankAccount.search([
            ('partner_id', '=', self.id),
            ('building_pay_managed', '=', True),
        ])
        old_accounts.unlink()

        # Crea il nuovo conto bancario
        BankAccount.create({
            'partner_id': self.id,
            'acc_number': iban_clean,
            'building_pay_managed': True,
        })
