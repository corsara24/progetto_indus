# Come attivare l'invio email reale (per la demo)

La dashboard può ora inviare davvero l'email di promemoria taratura, con conferma a schermo, invece di aprire solo il client di posta. Per farlo funzionare devi collegare un account email che spedisce per conto della dashboard.

## 1. Genera una "App Password" su Gmail (consigliato, 5 minuti)

Serve un account Gmail con la verifica in due passaggi attiva (puoi usarne uno nuovo creato apposta per la demo, così non tocchi la tua casella principale).

1. Vai su https://myaccount.google.com/security
2. Attiva "Verifica in due passaggi" se non è già attiva
3. Cerca "Password per le app" (App Passwords) nella stessa pagina
4. Crea una nuova app password (nome libero, es. "Dashboard Alstom")
5. Google ti mostra un codice di 16 caratteri: è quella la password da usare, **non** la tua password normale

## 2. Compila email_config.json

Apri il file `email_config.json` nella cartella del progetto con un editor di testo (es. Blocco Note) e compila:

- `mittente_email`: l'indirizzo Gmail che hai usato al punto 1
- `mittente_password_app`: il codice a 16 caratteri (senza spazi)
- `attivo`: cambia da `false` a `true`

Salva il file. Non serve altro: `smtp_host` e `smtp_porta` vanno già bene per Gmail.

## 3. Riavvia server.py

Chiudi e riapri `server.py`. Da questo momento, quando premi "📧 Invia email ora" nell'anteprima del promemoria, la mail parte davvero e vedrai la conferma a schermo con orario e destinatario — utile da mostrare in presentazione.

## Note

- Se lasci `attivo: false`, il pulsante di invio mostra un messaggio d'errore chiaro invece di provare a spedire: comodo se stai facendo altro e non vuoi email in giro per sbaglio.
- Questo file resta solo sul tuo PC: il server lo legge in locale, non viene mai caricato online.
- Se vuoi usare un account aziendale diverso da Gmail, dimmi l'host SMTP del tuo provider (es. Outlook/Office365 è `smtp.office365.com`, porta 587) e aggiorno io il file.
