# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Blocca la conferma se il partner principale non ha l'accordo caricato.

        Risale all'azienda/contatto radice ignorando gli indirizzi figlio,
        in modo che il controllo venga eseguito sul titolare del profilo
        portale e non sull'indirizzo di fatturazione specifico dell'ordine.
        """
        for order in self:
            root_partner = order.partner_id
            while root_partner.parent_id:
                root_partner = root_partner.parent_id

            if not root_partner.x_building_pay_accordo:
                raise UserError(_(
                    "Impossibile confermare l'ordine.\n\n"
                    "Il cliente '%(name)s' non ha ancora caricato "
                    "l'Accordo contrattuale con Progetti e Soluzioni. "
                    "Completare il profilo portale prima di procedere.",
                    name=root_partner.name,
                ))

        return super().action_confirm()
