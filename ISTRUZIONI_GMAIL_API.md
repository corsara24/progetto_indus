# Come attivare l'invio email con Gmail API (senza App Password)

Il tuo account Gmail non permette di creare una "Password per le app", quindi
il sistema è configurato per usare **Gmail API con OAuth2**: stesso risultato
(la dashboard e lo script promemoria mandano email per davvero), ma
l'autorizzazione avviene tramite login Google invece che con una password
da 16 caratteri.

Questa configurazione va fatta una sola volta, ed è l'unica parte che devi
fare tu: richiede il login al tuo account Google, che io non posso fare al
posto tuo.

## 1. Crea un progetto su Google Cloud Console

1. Vai su https://console.cloud.google.com/ e accedi con `simoneninetta2@gmail.com`
2. In alto, clicca sul selettore progetto → **Nuovo progetto**
3. Nome libero, es. "Monitoraggio Attrezzature" → **Crea**
4. Assicurati che il progetto appena creato sia selezionato in alto

## 2. Abilita la Gmail API

1. Vai su https://console.cloud.google.com/apis/library/gmail.googleapis.com
   (con il progetto giusto selezionato)
2. Clicca **Abilita**

## 3. Configura la schermata di consenso OAuth

1. Vai su https://console.cloud.google.com/apis/credentials/consent
2. Tipo utente: **Esterno** → **Crea**
3. Compila i campi obbligatori (nome app es. "Monitoraggio Attrezzature",
   email di supporto e email sviluppatore: usa `simoneninetta2@gmail.com`)
4. Salva e continua nelle schermate successive (Ambiti: puoi saltare,
   Utenti di test: **aggiungi `simoneninetta2@gmail.com`** come utente di
   test — importante, altrimenti Google blocca l'accesso)
5. Salva fino alla fine

## 4. Crea le credenziali OAuth

1. Vai su https://console.cloud.google.com/apis/credentials
2. **Crea credenziali** → **ID client OAuth**
3. Tipo di applicazione: **App desktop**
4. Nome libero, es. "Dashboard Alstom desktop" → **Crea**
5. Ti compare un popup: clicca **Scarica JSON**
6. Rinomina il file scaricato in `credenziali_google_oauth.json` e spostalo
   nella cartella del progetto: `C:\Users\Utente\Desktop\progetto indus\`
   (deve stare allo stesso livello di `server.py`)

## 5. Attiva e testa

1. Apri `email_config.json` e cambia `"attivo": false` in `"attivo": true`
2. Dimmi quando hai fatto tutti i passaggi sopra (compreso il file
   `credenziali_google_oauth.json` nella cartella) e faccio un invio di
   prova: al primo invio si aprirà il browser per il consenso — dovrai solo
   cliccare "Consenti" con l'account `simoneninetta2@gmail.com`, poi non
   servirà rifarlo (il token si salva in `token_google_oauth.json` e si
   rinnova da solo)

## Note di sicurezza

- `credenziali_google_oauth.json` e `token_google_oauth.json` restano solo
  sul tuo PC (sono già esclusi da Git tramite `.gitignore`) e **non vanno
  mai condivisi** — chi li ha può inviare email a nome tuo
- Se l'app resta in modalità "Test" (schermata di consenso), il token
  potrebbe scadere dopo 7 giorni e richiedere un nuovo consenso: se succede,
  dimmelo e vediamo se serve pubblicare l'app (bastano pochi click, resta
  comunque solo per uso tuo/interno)
