# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleBuildingPay(WebsiteSale):
    """Estende il checkout eCommerce con le regole BuildingPay.

    Gestisce:
    - Blocco del checkout se l'accordo contrattuale non è caricato
    - Filtro degli indirizzi di fatturazione: solo quelli con
      x_building_pay_abilitato = True vengono proposti all'utente
    - Controllo che l'indirizzo scelto sia abilitato prima di confermare
    """

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_building_pay_billing_addresses(self, partner):
        """Restituisce gli indirizzi di fatturazione abilitati BuildingPay.

        Cerca tra i contatti di tipo 'invoice' figli del partner corrente
        quelli con il flag x_building_pay_abilitato attivo.
        """
        return request.env['res.partner'].sudo().search([
            '|',
            ('id', '=', partner.id),
            ('parent_id', 'child_of', partner.id),
            ('type', '=', 'invoice'),
            ('x_building_pay_abilitato', '=', True),
        ])

    def _building_pay_check_accordo(self):
        """Verifica che l'utente corrente abbia caricato l'accordo contrattuale.

        Returns:
            True se l'accordo è presente o l'utente è pubblico, False altrimenti.
        """
        if request.env.user._is_public():
            return True
        return bool(request.env.user.partner_id.x_building_pay_accordo)

    # -------------------------------------------------------------------------
    # Override /shop/checkout
    # -------------------------------------------------------------------------

    @http.route(
        ['/shop/checkout'],
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def checkout(self, **post):
        """Blocca il checkout se l'accordo è mancante e inietta gli indirizzi filtrati."""
        if not self._building_pay_check_accordo():
            return request.redirect('/my/account?warning=accordo_mancante')

        response = super().checkout(**post)

        if hasattr(response, 'qcontext') and not request.env.user._is_public():
            partner = request.env.user.partner_id
            response.qcontext['building_pay_billing_addresses'] = (
                self._get_building_pay_billing_addresses(partner)
            )

        return response

    # -------------------------------------------------------------------------
    # Override /shop/address
    # -------------------------------------------------------------------------

    @http.route(
        ['/shop/address'],
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def address(self, **kw):
        """Inietta gli indirizzi BuildingPay nel contesto della pagina indirizzi."""
        response = super().address(**kw)

        if hasattr(response, 'qcontext') and not request.env.user._is_public():
            partner = request.env.user.partner_id
            response.qcontext['building_pay_billing_addresses'] = (
                self._get_building_pay_billing_addresses(partner)
            )

        return response

    # -------------------------------------------------------------------------
    # Override /shop/confirm_order
    # -------------------------------------------------------------------------

    @http.route(
        ['/shop/confirm_order'],
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def confirm_order(self, **post):
        """Verifica accordo e indirizzo di fatturazione prima della conferma."""
        if not self._building_pay_check_accordo():
            return request.redirect('/my/account?warning=accordo_mancante')

        order = request.website.sale_get_order()
        if order and order.partner_invoice_id:
            if not order.partner_invoice_id.x_building_pay_abilitato:
                # Sostituisce con il primo indirizzo abilitato disponibile
                partner = request.env.user.partner_id
                bp_addresses = self._get_building_pay_billing_addresses(partner)
                if bp_addresses:
                    order.sudo().write({'partner_invoice_id': bp_addresses[0].id})

        return super().confirm_order(**post)
