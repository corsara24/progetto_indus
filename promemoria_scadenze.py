#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Promemoria email per scadenze di taratura/revisione in arrivo.

Pensato per essere lanciato una volta all'accensione/login del PC (vedi
avvia_promemoria_scadenze.bat + Utilita' di pianificazione di Windows): non
serve un server sempre acceso. Ad ogni esecuzione legge dati_store.json e
invia un'email al responsabile di ogni attrezzatura la cui scadenza_revisione
cade entro i prossimi GIORNI_PREAVVISO giorni, riusando la stessa funzione di
invio SMTP di server.py (quindi va configurato email_config.json, vedi
ISTRUZIONI_EMAIL.md).

Le notifiche gia' inviate vengono registrate in
notifiche_promemoria_inviate.json, cosi' riaccendendo il PC piu' volte prima
della scadenza non si rispedisce la stessa email.

USO:
    python promemoria_scadenze.py
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from server import invia_email_promemoria  # noqa: E402  (riusa l'invio SMTP di server.py)

BASE_DIR = Path(__file__).resolve().parent
DATI_PATH = BASE_DIR / "dati_store.json"
REGISTRO_PATH = BASE_DIR / "notifiche_promemoria_inviate.json"
LOG_PATH = BASE_DIR / "log_promemoria_scadenze.txt"
GIORNI_PREAVVISO = 10

# Fase di test: invia sempre a questo indirizzo, ignorando responsabile_email/
# email_cc di dati_store.json (che contengono indirizzi fittizi/dimostrativi).
DESTINATARIO_TEST = "sararaimondo24@gmail.com"


def log(msg):
    riga = f"[{datetime.now():%d/%m/%Y %H:%M:%S}] {msg}"
    print(riga)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(riga + "\n")


def carica_registro():
    if not REGISTRO_PATH.exists():
        return {}
    try:
        with REGISTRO_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def salva_registro(registro):
    with REGISTRO_PATH.open("w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)


def corpo_email(a, giorni):
    testo = (
        f"Promemoria: l'attrezzatura {a['codice']} ({a['nome']}) ha la scadenza di "
        f"taratura/revisione il {a['scadenza_revisione']}, tra {giorni} giorno/i.\n\n"
        f"Ubicazione: {a.get('ubicazione') or '-'}\n"
        f"Responsabile: {a.get('responsabile_nome') or '-'}\n"
    )
    html = (
        f"<p>Promemoria: l'attrezzatura <b>{a['codice']}</b> ({a['nome']}) ha la scadenza di "
        f"taratura/revisione il <b>{a['scadenza_revisione']}</b>, tra <b>{giorni}</b> giorno/i.</p>"
        f"<p>Ubicazione: {a.get('ubicazione') or '-'}<br>"
        f"Responsabile: {a.get('responsabile_nome') or '-'}</p>"
    )
    return testo, html


def main():
    if not DATI_PATH.exists():
        log(f"ERRORE: {DATI_PATH.name} non trovato, controllo annullato.")
        return

    with DATI_PATH.open(encoding="utf-8") as f:
        store = json.load(f)

    oggi = date.today()
    registro = carica_registro()
    inviate = 0
    saltate = 0

    for a in store.get("attrezzature", []):
        codice = a.get("codice")
        scadenza_raw = a.get("scadenza_revisione")
        if not codice or not scadenza_raw:
            continue
        try:
            scadenza = datetime.strptime(scadenza_raw, "%Y-%m-%d").date()
        except ValueError:
            continue

        giorni = (scadenza - oggi).days
        if not (0 <= giorni <= GIORNI_PREAVVISO):
            continue

        chiave = f"{codice}|{scadenza_raw}"
        if chiave in registro:
            continue  # promemoria gia' inviato per questa scadenza

        destinatario = DESTINATARIO_TEST

        oggetto = f"Promemoria scadenza taratura - {codice} (tra {giorni} giorni)"
        corpo_testo, corpo_html = corpo_email(a, giorni)
        esito = invia_email_promemoria(destinatario, [], oggetto, corpo_testo, corpo_html)

        if esito.get("ok"):
            registro[chiave] = {"inviata_il": datetime.now().isoformat(timespec="seconds")}
            salva_registro(registro)
            log(f"{codice}: promemoria inviato a {destinatario} (scadenza tra {giorni}gg).")
            inviate += 1
        else:
            log(f"{codice}: invio fallito - {esito.get('errore')}")
            saltate += 1

    log(f"Controllo completato: {inviate} email inviate, {saltate} saltate.")


if __name__ == "__main__":
    main()
