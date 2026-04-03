# BuildingPay Portal

Modulo Odoo 17 EE che estende il portale clienti e il flusso eCommerce
con le funzionalità del servizio **BuildingPay**.

---

## Indice

- [Funzionalità](#funzionalità)
- [Struttura del modulo](#struttura-del-modulo)
- [Dipendenze](#dipendenze)
- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Flusso utente](#flusso-utente)
- [Ruoli e permessi](#ruoli-e-permessi)
- [Note tecniche](#note-tecniche)

---

## Funzionalità

### Indirizzo di fatturazione

Ogni indirizzo di fatturazione (`res.partner` con `type = invoice`) acquisisce
i seguenti campi aggiuntivi:

| Campo | Tipo | Descrizione |
|---|---|---|
| `x_building_pay_contratto` | Binary (attachment) | Documento contratto BuildingPay |
| `x_building_pay_contratto_filename` | Char | Nome file del contratto |
| `x_building_pay_contratto_caricato` | Boolean (readonly, computed) | Spuntato automaticamente quando il contratto è presente |
| `x_building_pay_iban` | Char | Codice IBAN — sincronizzato automaticamente su `res.partner.bank` |
| `x_building_pay_abilitato` | Boolean | Abilita l'indirizzo al servizio BuildingPay (solo Building Pay Manager) |

### Profilo portale (contatto principale)

| Campo | Tipo | Descrizione |
|---|---|---|
| `x_building_pay_accordo` | Binary (attachment) | Accordo contrattuale con Progetti e Soluzioni |
| `x_building_pay_accordo_filename` | Char | Nome file dell'accordo |

### Regole di business

- **Accordo obbligatorio**: se l'accordo non è caricato, l'utente portale
  non può accedere al checkout né confermare un ordine.
- **Checkout filtrato**: in fase di acquisto, la selezione dell'indirizzo
  di fatturazione mostra solo i contatti con `x_building_pay_abilitato = True`.
- **Intestazione fattura**: il nome sull'intestazione del PDF riporta solo
  il nome del contatto figlio, senza il prefisso dell'azienda padre
  (comportamento di default di Odoo: `"Padre, Figlio"`).
- **Sincronizzazione IBAN**: al salvataggio di `x_building_pay_iban`,
  il modulo crea o aggiorna automaticamente il record `res.partner.bank`
  corrispondente, rimuovendo eventuali conti BuildingPay precedenti.

---

## Struttura del modulo

```
building_pay/
├── __init__.py
├── __manifest__.py
│
├── models/
│   ├── __init__.py
│   ├── res_partner_bank.py      # Campo building_pay_managed su res.partner.bank
│   ├── res_partner.py           # Campi BuildingPay + sync IBAN
│   ├── sale_order.py            # Blocco conferma ordine se accordo mancante
│   └── account_move.py          # Campo nome intestatario senza padre
│
├── controllers/
│   ├── __init__.py
│   ├── portal.py                # Upload accordo + salvataggio indirizzo
│   └── website_sale.py          # Checkout filtrato + blocco accordo
│
├── security/
│   ├── building_pay_groups.xml  # Categoria e gruppo Building Pay Manager
│   └── ir.model.access.csv
│
├── views/
│   ├── res_partner_views.xml            # Tab BuildingPay nel form backend
│   ├── portal_templates.xml             # Accordo nel profilo + form indirizzo
│   ├── website_sale_templates.xml       # Banner warning nel checkout
│   └── report_invoice_building_pay.xml  # Override nome sul PDF fattura
│
└── static/
    ├── description/
    │   └── index.html           # Pagina App Store Odoo
    └── src/js/
        └── portal_building_pay.js  # Widget frontend
```

---

## Dipendenze

```python
'depends': ['portal', 'website_sale', 'account', 'sale']
```

Odoo 17 **Enterprise Edition** richiesto.

---

## Installazione

1. Copia la cartella `building_pay` nella directory `addons` del tuo Odoo
   (o nel path configurato in `addons_path`).

2. Verifica che il nome della cartella sia `building_pay`
   (underscore, non trattini).

3. Aggiorna la lista dei moduli:
   **Impostazioni → Attiva modalità sviluppatore → Aggiorna lista app**

4. Cerca `BuildingPay Portal` e clicca **Installa**.

5. Riavvia il server se necessario:
   ```bash
   ./odoo-bin -u building_pay -d <nome_database>
   ```

---

## Configurazione

### 1. Assegnare il ruolo Building Pay Manager

Vai in **Impostazioni → Utenti e aziende → Utenti**, apri l'utente
che deve gestire le abilitazioni e spunta il ruolo
**BuildingPay → Building Pay Manager**.

### 2. Abilitare un indirizzo di fatturazione

1. Dal backend, apri il record `res.partner` del cliente.
2. Vai nel tab **BuildingPay**.
3. Carica il contratto nel campo **Contratto**.
4. Inserisci l'**IBAN** (verrà creato automaticamente il conto bancario).
5. Spunta **Abilitato al servizio BuildingPay**
   *(visibile solo agli utenti con ruolo Building Pay Manager)*.

### 3. Verifica degli xpath dei template

In caso di aggiornamenti Odoo EE, gli xpath nei template XML potrebbero
richiedere un adattamento. Verificare con i DevTools del browser:

| Template | xpath da verificare |
|---|---|
| `portal_templates.xml` | `//div[hasclass('o_portal_details')]` |
| `portal_templates.xml` | `//form[hasclass('o_portal_address_form')]` |
| `report_invoice_building_pay.xml` | `//span[@t-field='o.partner_id.display_name']` |

Per il report, verificare con:
```bash
./odoo-bin --dev=xml -d <database>
```

---

## Flusso utente

```
Utente portale
    │
    ├─ 1. Accede a /my/account
    │       └─ Carica l'Accordo contrattuale con Progetti e Soluzioni
    │
    ├─ 2. Aggiunge un indirizzo di fatturazione
    │       ├─ Carica il documento Contratto
    │       └─ Inserisce l'IBAN
    │
    ├─ 3. L'amministratore (Building Pay Manager) abilita l'indirizzo
    │
    ├─ 4. Aggiunge prodotti al carrello e va al checkout
    │       └─ Seleziona l'indirizzo di fatturazione abilitato BuildingPay
    │
    └─ 5. Conferma l'ordine
            └─ La fattura generata riporta solo il nome del contatto figlio
```

---

## Ruoli e permessi

| Ruolo | Può fare |
|---|---|
| **Utente Portale** | Caricare accordo e contratto, inserire IBAN, vedere stato abilitazione (readonly) |
| **Building Pay Manager** | Tutto sopra + abilitare/disabilitare il servizio sull'indirizzo |
| **Amministratore** | Gestione completa + assegnazione ruoli |

---

## Note tecniche

### Sincronizzazione IBAN

La logica è in `models/res_partner.py → _sync_building_pay_bank_account()`.
Viene invocata automaticamente dai metodi `create` e `write` quando il campo
`x_building_pay_iban` è incluso nei valori. Il flag `building_pay_managed`
su `res.partner.bank` permette di distinguere i conti creati da questo modulo
da quelli inseriti manualmente.

### Nome intestatario fattura

Il campo `x_building_pay_partner_name` su `account.move` è computed + stored
e dipende da `partner_id.name`. Contiene sempre il nome del solo contatto
(senza padre), a differenza di `partner_id.display_name` che Odoo restituisce
nel formato `"Padre, Figlio"`. Il template del report fattura usa questo campo
al posto del `display_name` standard.

### Blocco checkout

Il blocco avviene a due livelli:
1. **Controller** (`WebsiteSaleBuildingPay.checkout`): redirect a `/my/account`
   prima che la pagina venga renderizzata.
2. **Template** (`website_sale_templates.xml`): banner di avviso visivo
   nel caso in cui il template venga raggiunto da altri percorsi.

### Cumulo degli override su /shop/checkout

`WebsiteSaleBuildingPay` eredita da `WebsiteSale` (non da `CustomerPortal`).
Il controller `portal.py` gestisce esclusivamente le route BuildingPay
(`/building_pay/*`) e non sovrascrive route website_sale.
