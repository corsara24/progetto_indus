#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Invio email tramite Gmail API con OAuth2 — alternativa a SMTP + App Password,
utile quando l'account Google non permette di creare una "Password per le
app" (es. account con solo passkey come verifica in due passaggi).

Setup richiesto una tantum (fatto dall'utente su Google Cloud Console, vedi
ISTRUZIONI_GMAIL_API.md per i passaggi dettagliati):
  1. Crea un progetto su https://console.cloud.google.com/
  2. Abilita la "Gmail API"
  3. Configura la schermata di consenso OAuth (tipo "Esterno", aggiungi il
     tuo indirizzo Gmail come "utente di test")
  4. Crea credenziali -> "ID client OAuth" -> tipo applicazione "Desktop app"
  5. Scarica il JSON e salvalo in questa cartella come
     credenziali_google_oauth.json

Alla prima email inviata si apre il browser per il consenso: dopo aver
autorizzato una volta, il token viene salvato in token_google_oauth.json e
riusato/rinnovato automaticamente, senza richiedere login ad ogni invio.
"""

import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CREDENZIALI_PATH = BASE_DIR / "credenziali_google_oauth.json"
TOKEN_PATH = BASE_DIR / "token_google_oauth.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _ottieni_credenziali():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENZIALI_PATH.exists():
                raise FileNotFoundError(
                    f"Manca {CREDENZIALI_PATH.name}: scaricalo da Google Cloud Console "
                    "(vedi ISTRUZIONI_GMAIL_API.md) e mettilo in questa cartella."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENZIALI_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    return creds


def invia_email_gmail_api(mittente_email, mittente_nome, destinatario, cc, oggetto, corpo_testo, corpo_html=None):
    """Invia un'email tramite Gmail API (OAuth2). Ritorna sempre un dict con
    almeno la chiave "ok", nella stessa forma di invia_email_promemoria() in
    server.py, cosi' server.py puo' usarla come sostituto trasparente senza
    mai sollevare eccezioni verso il chiamante."""
    if not destinatario:
        return {"ok": False, "errore": "Nessun indirizzo email del responsabile impostato per questa attrezzatura."}

    try:
        from googleapiclient.discovery import build
    except ImportError:
        return {"ok": False, "errore": "Librerie Google mancanti: esegui 'pip install -r requirements.txt'."}

    try:
        creds = _ottieni_credenziali()
    except FileNotFoundError as e:
        return {"ok": False, "errore": str(e)}
    except Exception as e:
        return {"ok": False, "errore": f"Errore di autenticazione Google: {e}"}

    msg = MIMEMultipart("alternative")
    msg["Subject"] = oggetto
    msg["From"] = f"{mittente_nome} <{mittente_email}>" if mittente_nome else mittente_email
    msg["To"] = destinatario
    cc_puliti = [c.strip() for c in (cc or []) if c and c.strip()]
    if cc_puliti:
        msg["Cc"] = ", ".join(cc_puliti)
    msg.attach(MIMEText(corpo_testo or "", "plain", "utf-8"))
    if corpo_html:
        msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    try:
        service = build("gmail", "v1", credentials=creds)
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
    except Exception as e:
        return {"ok": False, "errore": f"Errore durante l'invio con Gmail API: {e}"}

    return {
        "ok": True,
        "destinatario": destinatario,
        "cc": cc_puliti,
        "orario": datetime.now().strftime("%H:%M:%S"),
        "mittente": mittente_email,
    }
