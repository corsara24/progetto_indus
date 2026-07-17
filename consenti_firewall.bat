@echo off
echo ============================================================
echo  Sblocca l'accesso alla Dashboard Attrezzature dalla rete
echo ============================================================
echo.
echo Questo script aggiunge una regola al Firewall di Windows per
echo permettere ad altri dispositivi (es. smartphone) sulla stessa
echo rete Wi-Fi di collegarsi alla dashboard (porta 8000).
echo.
echo IMPORTANTE: deve essere eseguito come Amministratore.
echo Se non hai fatto clic destro - "Esegui come amministratore",
echo chiudi questa finestra e riprovare cosi'.
echo.
pause

netsh advfirewall firewall show rule name="Dashboard Attrezzature Alstom" >nul 2>&1
if %errorlevel%==0 (
    echo Regola gia' presente, la aggiorno...
    netsh advfirewall firewall delete rule name="Dashboard Attrezzature Alstom" >nul 2>&1
)

netsh advfirewall firewall add rule name="Dashboard Attrezzature Alstom" dir=in action=allow protocol=TCP localport=8000 profile=any

if %errorlevel%==0 (
    echo.
    echo Fatto! La porta 8000 e' ora consentita nel Firewall di Windows.
    echo Ora riavvia server.py (se era gia' avviato, chiudilo e riaprilo^)
    echo e riprova a collegarti dallo smartphone.
) else (
    echo.
    echo Non sono riuscito ad aggiungere la regola.
    echo Assicurati di aver eseguito questo file come Amministratore
    echo (clic destro sul file - "Esegui come amministratore"^).
)
echo.
pause
