# -*- coding: utf-8 -*-

import base64

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class BuildingPayPortal(CustomerPortal):
    """Estende il portale clienti con le funzionalità BuildingPay.

    Gestisce:
    - Upload dell'accordo contrattuale nel profilo generale
    - Salvataggio di contratto e IBAN sugli indirizzi di fatturazione
    """

    def _prepare_portal_layout_values(self):
        """Aggiunge il partner corrente al contesto dei template portale."""
        values = super()._prepare_portal_layout_values()
        values['partner'] = request.env.user.partner_id
        return values

    # -------------------------------------------------------------------------
    # Route: upload accordo contrattuale (profilo generale)
    # -------------------------------------------------------------------------

    @http.route(
        '/building_pay/upload_accordo',
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def upload_accordo(self, accordo_file=None, **kwargs):
        """Carica l'accordo contrattuale con Progetti e Soluzioni.

        Il file viene salvato come attachment sul partner dell'utente corrente.
        """
        partner = request.env.user.partner_id

        if accordo_file and getattr(accordo_file, 'filename', None):
            content = accordo_file.read()
            if content:
                partner.sudo().write({
                    'x_building_pay_accordo': base64.b64encode(content),
                    'x_building_pay_accordo_filename': accordo_file.filename,
                })

        return request.redirect('/my/account')

    # -------------------------------------------------------------------------
    # Route: salvataggio campi BuildingPay sull'indirizzo di fatturazione
    # -------------------------------------------------------------------------

    @http.route(
        '/building_pay/save_address',
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def save_address_building_pay(
        self, partner_id=None, contratto_file=None, building_pay_iban=None, **kwargs
    ):
        """Salva contratto e IBAN su un indirizzo di fatturazione.

        Il write su x_building_pay_iban innesca automaticamente
        _sync_building_pay_bank_account nel model res.partner.
        """
        current_partner = request.env.user.partner_id
        vals = {}

        address = self._get_and_validate_address(partner_id, current_partner)
        if address is None:
            return request.redirect('/my/account')

        if contratto_file and getattr(contratto_file, 'filename', None):
            content = contratto_file.read()
            if content:
                vals['x_building_pay_contratto'] = base64.b64encode(content)
                vals['x_building_pay_contratto_filename'] = contratto_file.filename

        if building_pay_iban and building_pay_iban.strip():
            vals['x_building_pay_iban'] = building_pay_iban.strip()

        if vals:
            address.sudo().write(vals)

        return request.redirect('/my/account')

    @http.route(
        '/building_pay/save_address_and_redirect',
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def save_address_and_redirect(
        self, partner_id=None, contratto_file=None, building_pay_iban=None, **kwargs
    ):
        """Punto di ingresso dal form di modifica indirizzo nel portale.

        Salva i campi BuildingPay e poi reindirizza al profilo.
        I campi anagrafici standard (nome, città, ecc.) vengono
        gestiti separatamente dal controller nativo /my/address.
        """
        self.save_address_building_pay(
            partner_id=partner_id,
            contratto_file=contratto_file,
            building_pay_iban=building_pay_iban,
            **kwargs,
        )
        return request.redirect('/my/account')

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_and_validate_address(self, partner_id, current_partner):
        """Recupera e valida che l'indirizzo appartenga al partner corrente.

        Returns:
            res.partner record se valido, None altrimenti.
        """
        if not partner_id:
            return None

        address = request.env['res.partner'].sudo().browse(int(partner_id))
        if not address.exists():
            return None

        # Risale alla radice dell'albero dei partner per il controllo di ownership
        root = address
        while root.parent_id:
            root = root.parent_id

        if root.id != current_partner.id and address.id != current_partner.id:
            return None

        return address
