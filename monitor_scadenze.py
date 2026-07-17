#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend di monitoraggio scadenze attrezzature.

Ogni N secondi (default 60 = 1 minuto) legge il file "dati_store.json" (la
stessa fonte dati usata dal server della dashboard: server.py), individua le
attrezzature la cui scadenza di taratura/revisione cade nella settimana
corrente (lunedi-domenica) e rigenera un report HTML con la tabella dei
codici interessati. Cosi' il report riflette anche gli interventi/tarature
registrati dalla dashboard, non solo i dati di partenza.

USO:
    python monitor_scadenze.py            # loop continuo, controllo ogni 60s
    python monitor_scadenze.py --once      # esegue un solo controllo ed esce
    python monitor_scadenze.py --interval 30   # cambia l'intervallo (secondi)

PROSSIMA IMPLEMENTAZIONE (non ancora attiva):
    La funzione invia_email() e' gia' predisposta come punto di innesto:
    andra' completata con l'invio SMTP reale (vedi TODO al suo interno).
"""

import argparse
import html
import json
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

# --------------------------------------------------------------------------
# Configurazione
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATI_PATH = BASE_DIR / "dati_store.json"
OUTPUT_HTML = BASE_DIR / "scadenze_settimana.html"
DEFAULT_INTERVAL_SECONDS = 60


# --------------------------------------------------------------------------
# Logica di dominio
# --------------------------------------------------------------------------
def settimana_corrente(oggi: date):
    """Ritorna (lunedi, domenica) della settimana ISO che contiene 'oggi'."""
    lunedi = oggi - timedelta(days=oggi.weekday())
    domenica = lunedi + timedelta(days=6)
    return lunedi, domenica


def leggi_attrezzature(path: Path):
    """Legge dati_store.json e ritorna una lista di dict con date gia' parsate."""
    with open(path, encoding="utf-8") as f:
        store = json.load(f)

    attrezzature = []
    for a in store.get("attrezzature", []):
        codice = a.get("codice")
        scadenza_raw = a.get("scadenza_revisione")
        if not codice or not scadenza_raw:
            continue
        scadenza = datetime.strptime(scadenza_raw, "%Y-%m-%d").date()

        ultimo_raw = a.get("ultimo_controllo")
        ultimo = datetime.strptime(ultimo_raw, "%Y-%m-%d").date() if ultimo_raw else None

        attrezzature.append({
            "codice": str(codice),
            "nome": a.get("nome") or "",
            "ubicazione": a.get("ubicazione") or "",
            "ultimo_controllo": ultimo,
            "scadenza": scadenza,
        })
    return attrezzature


def trova_scaduti_settimana(attrezzature, oggi: date):
    """Filtra le attrezzature la cui scadenza cade nella settimana corrente."""
    lunedi, domenica = settimana_corrente(oggi)
    scaduti = []
    for a in attrezzature:
        if lunedi <= a["scadenza"] <= domenica:
            giorni = (oggi - a["scadenza"]).days
            scaduti.append({**a, "giorni": giorni})
    scaduti.sort(key=lambda a: a["scadenza"])
    return scaduti, lunedi, domenica


# --------------------------------------------------------------------------
# Generazione HTML
# --------------------------------------------------------------------------
def _fmt(d):
    return d.strftime("%d/%m/%Y") if d else "—"


def _giorni_label(giorni):
    if giorni > 0:
        return f"Scaduta da {giorni} gg"
    if giorni == 0:
        return "Scade oggi"
    return f"Scade tra {abs(giorni)} gg"


def genera_html(scaduti, lunedi, domenica, generato_il, dati_mtime):
    righe_html = ""
    if scaduti:
        for a in scaduti:
            stato_class = "rosso" if a["giorni"] >= 0 else "giallo"
            righe_html += f"""
      <tr>
        <td><b>{html.escape(a['codice'])}</b></td>
        <td>{html.escape(str(a['nome']))}</td>
        <td>{html.escape(str(a['ubicazione']))}</td>
        <td>{_fmt(a['ultimo_controllo'])}</td>
        <td>{_fmt(a['scadenza'])}</td>
        <td><span class="pill {stato_class}">{_giorni_label(a['giorni'])}</span></td>
      </tr>"""
    else:
        righe_html = """
      <tr><td colspan="6" class="empty">Nessuna scadenza di taratura/revisione questa settimana.</td></tr>"""

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Scadenze della settimana - Monitoraggio Attrezzature</title>
<meta http-equiv="refresh" content="60">
<style>
  body{{margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif; background:#f8fafc; color:#111827;}}
  .wrap{{max-width:960px; margin:0 auto; padding:30px 20px 60px;}}
  header{{background:#182C4C; color:#fff; padding:20px 26px; border-radius:10px 10px 0 0; border-bottom:4px solid #E3312B;}}
  header h1{{margin:0 0 6px; font-size:1.3rem;}}
  header .sub{{color:#cbd5e1; font-size:0.85rem;}}
  .meta{{background:#fff; border:1px solid #e5e7eb; border-top:none; padding:14px 26px; font-size:0.82rem; color:#6b7280;}}
  table{{width:100%; border-collapse:collapse; background:#fff; border:1px solid #e5e7eb; border-top:none;}}
  thead th{{background:#f3f4f6; color:#182C4C; font-size:0.72rem; text-transform:uppercase; letter-spacing:.03em; padding:10px; text-align:left; border-bottom:2px solid #e5e7eb;}}
  tbody td{{padding:10px; border-bottom:1px solid #e5e7eb; font-size:0.88rem;}}
  tbody tr:last-child td{{border-bottom:none;}}
  .empty{{text-align:center; color:#6b7280; padding:24px; font-style:italic;}}
  .pill{{display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.74rem; font-weight:700;}}
  .pill.rosso{{background:#fee2e2; color:#7f1d1d;}}
  .pill.giallo{{background:#fef9c3; color:#713f12;}}
  footer{{margin-top:16px; color:#9ca3af; font-size:0.74rem; text-align:center;}}
  .count{{font-weight:700; color:#E3312B;}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Scadenze della settimana</h1>
    <div class="sub">Settimana dal {_fmt(lunedi)} al {_fmt(domenica)} — <span class="count">{len(scaduti)}</span> attrezzatura/e con scadenza in questo periodo</div>
  </header>
  <div class="meta">
    Report generato il {generato_il.strftime('%d/%m/%Y alle %H:%M:%S')} · sorgente dati: dati_store.json (ultima modifica: {dati_mtime.strftime('%d/%m/%Y %H:%M:%S')}) · aggiornamento automatico ogni minuto
  </div>
  <table>
    <thead>
      <tr>
        <th>Codice</th><th>Attrezzatura</th><th>Ubicazione</th><th>Ultimo controllo</th><th>Scadenza</th><th>Stato</th>
      </tr>
    </thead>
    <tbody>{righe_html}
    </tbody>
  </table>
  <footer>Prossima implementazione: invio automatico di questa tabella via email ai responsabili.</footer>
</div>
</body>
</html>"""


def scrivi_html(contenuto: str, path: Path):
    """Scrittura atomica: scrive su file temporaneo poi rinomina."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(contenuto, encoding="utf-8")
    tmp.replace(path)


# --------------------------------------------------------------------------
# Punto di innesto per la prossima implementazione (invio email)
# --------------------------------------------------------------------------
def invia_email(scaduti):
    """
    TODO (prossima implementazione): inviare la tabella via email reale.
    Idee per l'implementazione futura:
      - usare smtplib + email.mime.multipart per costruire il messaggio,
      - recuperare destinatario/CC per ciascun codice (vedi email_cc /
        responsabile_email gia' presenti nel dataset della dashboard HTML),
      - riusare genera_html()/una variante "solo tabella" come corpo HTML,
      - inviare una sola email cumulativa con tutti i codici scaduti,
        oppure una email per attrezzatura (da decidere con l'utente).
    Per ora questa funzione non fa nulla: e' un placeholder.
    """
    pass


# --------------------------------------------------------------------------
# Ciclo principale
# --------------------------------------------------------------------------
def esegui_controllo():
    oggi = date.today()
    generato_il = datetime.now()
    dati_mtime = datetime.fromtimestamp(DATI_PATH.stat().st_mtime)

    attrezzature = leggi_attrezzature(DATI_PATH)
    scaduti, lunedi, domenica = trova_scaduti_settimana(attrezzature, oggi)

    contenuto = genera_html(scaduti, lunedi, domenica, generato_il, dati_mtime)
    scrivi_html(contenuto, OUTPUT_HTML)

    invia_email(scaduti)  # placeholder, non attivo

    print(f"[{generato_il:%d/%m/%Y %H:%M:%S}] Controllo eseguito - "
          f"{len(scaduti)} attrezzatura/e scadute nella settimana "
          f"{_fmt(lunedi)}-{_fmt(domenica)} -> {OUTPUT_HTML.name} aggiornato")

    return scaduti


def main():
    parser = argparse.ArgumentParser(description="Backend di monitoraggio scadenze attrezzature.")
    parser.add_argument("--once", action="store_true", help="Esegue un solo controllo ed esce.")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS,
                         help="Intervallo tra i controlli, in secondi (default: 60).")
    args = parser.parse_args()

    if not DATI_PATH.exists():
        print(f"ERRORE: file non trovato: {DATI_PATH}", file=sys.stderr)
        print("Avvia almeno una volta 'python server.py' per crearlo, oppure verifica il percorso.", file=sys.stderr)
        sys.exit(1)

    print(f"Backend monitoraggio scadenze avviato. File sorgente: {DATI_PATH}")
    print(f"Report generato in: {OUTPUT_HTML}")
    print(f"Intervallo di controllo: {args.interval}s" + ("" if not args.once else " (modalita' --once: un solo giro)"))

    if args.once:
        esegui_controllo()
        return

    try:
        while True:
            try:
                esegui_controllo()
            except (PermissionError, json.JSONDecodeError):
                print("Attenzione: dati_store.json in scrittura in questo momento. Riprovo al prossimo giro.")
            except Exception as e:
                print(f"Errore durante il controllo: {e}", file=sys.stderr)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nBackend arrestato dall'utente.")


if __name__ == "__main__":
    main()
