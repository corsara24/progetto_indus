# Promemoria automatico scadenze (via email, all'accensione del PC)

`promemoria_scadenze.py` controlla `dati_store.json` e invia un'email al responsabile
di ogni attrezzatura la cui scadenza di taratura/revisione cade entro i prossimi
10 giorni. Non serve un server acceso 24/7: basta farlo partire una volta ad ogni
accensione/login del PC.

Tiene un registro (`notifiche_promemoria_inviate.json`) delle email già inviate,
così riaccendendo il PC più volte prima della scadenza non arrivano email doppie.
Ogni esecuzione viene anche annotata in `log_promemoria_scadenze.txt`, utile per
controllare che sia partito e cosa ha fatto.

## Prerequisito

Serve `email_config.json` compilato e con `"attivo": true` (vedi `ISTRUZIONI_EMAIL.md`).
Finché non lo attivi, lo script gira comunque ma registra nel log "invio non
attivato" invece di spedire.

## Come metterlo in esecuzione automatica all'accensione (Windows)

1. Apri **Utilità di pianificazione** (cerca "Utilità di pianificazione" o
   "Task Scheduler" nel menu Start).
2. Nel pannello a destra clicca **Crea attività di base...**
3. Nome: es. `Promemoria scadenze attrezzature` → **Avanti**
4. Trigger: scegli **All'accesso** (si attiva ad ogni login utente) → **Avanti**
5. Azione: scegli **Avvia un programma** → **Avanti**
6. In "Programma o script" clicca **Sfoglia...** e seleziona:
   `avvia_promemoria_scadenze.bat` nella cartella del progetto
   (`C:\Users\Utente\Desktop\progetto indus\`)
7. **Avanti** → **Fine**

Fatto: da ora, ogni volta che accendi/sblocchi il PC, il controllo parte in
automatico e in background (nessuna finestra visibile, usa `pythonw.exe`).

## Verifica che funzioni

- Controlla `log_promemoria_scadenze.txt` dopo il prossimo login: deve comparire
  una riga tipo `Controllo completato: N email inviate, N saltate.`
- Per testarlo subito senza aspettare un riavvio, apri l'Utilità di pianificazione,
  trova l'attività nell'elenco (**Libreria Utilità di pianificazione**) e clicca
  **Esegui** dal pannello a destra.
- Per un test manuale da terminale: `python promemoria_scadenze.py`

## Se vuoi cambiare il preavviso (default 10 giorni)

Apri `promemoria_scadenze.py` e modifica il valore di `GIORNI_PREAVVISO` in cima
al file.
