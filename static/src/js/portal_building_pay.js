/** @odoo-module **/
/**
 * BuildingPay — Frontend Widget
 *
 * Gestisce lato client:
 * 1. Nasconde nel checkout gli indirizzi di fatturazione non BuildingPay
 * 2. Mostra un messaggio se nessun indirizzo è disponibile
 * 3. Mostra l'alert accordo mancante se presente nel query string
 */
 
import publicWidget from '@web/legacy/js/public/public_widget';
 
publicWidget.registry.BuildingPayCheckout = publicWidget.Widget.extend({
    selector: '.oe_website_sale, .o_portal_wrap',
 
    start() {
        this._super(...arguments);
        this._filterBillingAddresses();
        this._showAccordoWarning();
    },
 
    /**
     * Nasconde le card degli indirizzi di fatturazione che non sono
     * abilitate BuildingPay (data-building-pay="False").
     * Aggiunge un alert se dopo il filtro non rimane nessun indirizzo.
     */
    _filterBillingAddresses() {
        const items = document.querySelectorAll('[data-building-pay]');
        if (!items.length) return;
 
        let visible = 0;
        items.forEach((el) => {
            if (el.dataset.buildingPay === 'True') {
                visible++;
            } else {
                el.style.display = 'none';
            }
        });
 
        if (visible === 0) {
            const container =
                document.querySelector('#billing_address_list') ||
                document.querySelector('.o_billing_address');
            if (container) {
                const alert = document.createElement('div');
                alert.className = 'alert alert-warning mt-2';
                alert.setAttribute('role', 'alert');
                alert.innerHTML =
                    '<i class="fa fa-exclamation-triangle me-2"></i>' +
                    '<strong>Nessun indirizzo di fatturazione abilitato.</strong> ' +
                    'Contatta l\'amministratore per abilitare un indirizzo ' +
                    'al servizio BuildingPay.';
                container.prepend(alert);
            }
        }
    },
 
    /**
     * Controlla il query string per ?warning=accordo_mancante
     * e inserisce un banner di errore in cima alla pagina.
     */
    _showAccordoWarning() {
        const params = new URLSearchParams(window.location.search);
        if (params.get('warning') !== 'accordo_mancante') return;
 
        const alert = document.createElement('div');
        alert.className =
            'alert alert-danger alert-dismissible d-flex align-items-center mt-3';
        alert.setAttribute('role', 'alert');
        alert.innerHTML =
            '<i class="fa fa-ban fa-lg me-3 flex-shrink-0"></i>' +
            '<div>' +
            '<strong>Attenzione!</strong> ' +
            'Devi caricare l\'<strong>Accordo contrattuale con Progetti e Soluzioni</strong> ' +
            'prima di poter effettuare un ordine.' +
            '</div>' +
            '<button type="button" class="btn-close ms-auto" ' +
            'data-bs-dismiss="alert" aria-label="Chiudi"></button>';
 
        const target =
            document.querySelector('#building_pay_accordo_section') ||
            document.querySelector('.o_portal_details') ||
            document.querySelector('main .container');
 
        if (target) {
            target.insertAdjacentElement('beforebegin', alert);
            alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    },
});
 
export default publicWidget.registry.BuildingPayCheckout;
