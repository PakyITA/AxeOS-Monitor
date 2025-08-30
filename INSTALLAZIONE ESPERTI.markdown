# Guida all'installazione e avvio di AxeOS Monitor

**AxeOS Monitor** è un bot Telegram per il monitoraggio e la gestione di miner di criptovalute, con supporto per prese smart Meross, Sonoff e Tuya. Questa guida ti guiderà passo-passo nell'installazione di Python, delle dipendenze necessarie e nell'avvio dello script `axeos_monitor.py` su Windows, macOS o Linux.

## Prerequisiti

- Un computer con accesso a Internet.
- Un bot Telegram configurato (crea un bot tramite [BotFather](https://t.me/BotFather) per ottenere il token).
- Un chat ID Telegram (puoi ottenerlo inviando un messaggio al bot e verificandolo tramite l'API Telegram).
- (Opzionale) Dispositivi smart Meross, Sonoff o Tuya configurati sulla tua rete WiFi (solo 2.4 GHz).
- Un miner con API accessibile (es. URL come `http://192.168.1.3/api/system/info`).

## Passo 1: Installare Python

### Windows
1. Scarica l'ultima versione di Python (3.11) da [python.org](https://www.python.org/downloads/).
   - Consigliato: Python 3.11.
2. Esegui il programma di installazione:
   - Spunta l'opzione **"Add Python to PATH"** durante l'installazione.
   - Scegli "Install Now" o personalizza il percorso di installazione.
3. Verifica l'installazione aprendo il Prompt dei comandi (`cmd`) e digitando:
   ```bash
   python --version
   ```
   Dovresti vedere qualcosa come `Python 3.11.4`.

### macOS
1. Python è spesso preinstallato, ma potrebbe essere una versione vecchia. Verifica con:
   ```bash
   python3 --version
   ```
2. Se la versione è inferiore a 3.8 o non è installata, scarica Python da [python.org](https://www.python.org/downloads/) o usa Homebrew:
   ```bash
   brew install python3.11
   ```
3. Verifica l'installazione:
   ```bash
   python3 --version
   ```

### Linux (Ubuntu/Debian)
1. Aggiorna i pacchetti:
   ```bash
   sudo apt update
   ```
2. Installa Python 3 e pip:
   ```bash
   sudo apt install python3 python3-pip
   ```
3. Verifica l'installazione:
   ```bash
   python3 --version
   pip3 --version
   ```

## Passo 2: Configurare un ambiente virtuale (opzionale, ma consigliato)

Un ambiente virtuale isola le dipendenze del progetto, evitando conflitti con altri pacchetti.

1. Crea una directory per il progetto:
   ```bash
   mkdir axeos_monitor
   cd axeos_monitor
   ```

2. Crea un ambiente virtuale:
   - Windows:
     ```bash
     python3.11 -m venv venv
     ```
   - macOS/Linux:
     ```bash
     python3.11 -m venv venv
     ```

3. Attiva l'ambiente virtuale:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   Dopo l'attivazione, vedrai `(venv)` nel terminale.

   Aggiornare pip:
   ```
   python3 -m pip install --upgrade pip
   
   ```

Eseguire l'upgrade di pip (potrebbe risultare necessario per il corretto funzionamento):
   ```
   pip install --upgrade pip
   ```


## Passo 3: Installare le dipendenze

Lo script richiede diverse librerie Python elencate nel file `requirements.txt`. Segui questi passaggi:

1. Crea un file `requirements.txt` nella directory del progetto con il seguente contenuto (IL FILE DOVREBBE ESSERE GIA' PRESENTE):
   ```
   python-telegram-bot>=20.0
   meross_iot
   tinytuya
   requests

   ```
   **Nota**: Le librerie `apscheduler`, `beautifulsoup4`, `playwright` e `matplotlib` non sono necessarie per lo script attuale, quindi non sono incluse. Se le usi per altre funzionalità, aggiungile al file.

2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

3. Verifica l'installazione:
   ```bash
   pip list
   ```
   Cerca `python-telegram-bot`, `requests`, `meross-iot` e `tinytuya` nell'elenco.

### Risoluzione dei problemi
- **Errore `pip not found`**:
  - Su Windows, usa `python -m pip install -r requirements.txt`.
  - Su macOS/Linux, usa `python3 -m pip install -r requirements.txt`.
- **Problemi di rete**:
  - Aggiungi `--trusted-host pypi.org --trusted-host files.pythonhosted.org` al comando `pip install` se riscontri errori di connessione.
- **Versione Python non compatibile**:
  - Assicurati di usare Python 3.8 o superiore (`python --version` o `python3 --version`).

## Passo 4: Configurare i dispositivi smart (opzionale)

Se vuoi controllare le prese smart Meross, Sonoff o Tuya, configura i dispositivi come segue:

### Meross
1. Configura la presa nell'app Meross (scaricabile da App Store/Play Store).
2. Annota:
   - **Email** e **password** del tuo account Meross.
   - **Nome esatto** della presa come appare nell'app Meross (es. "Presa Miner 1").
3. Assicurati che la presa sia sulla stessa rete WiFi del computer (solo 2.4 GHz).

### Sonoff
1. Configura la presa nell'app eWeLink (scaricabile da App Store/Play Store).
2. Annota:
   - **IP** della presa (verifica nel router o usa uno scanner di rete come `nmap`).
   - **Token** (ottenibile tramite eWeLink o, se usi Tasmota, dall'interfaccia web del dispositivo).
3. (Opzionale) Per il controllo locale, abilita la modalità DIY sul dispositivo Sonoff (consulta la documentazione Sonoff).

### Tuya
1. Configura la presa nell'app Tuya Smart o Smart Life (scaricabile da App Store/Play Store).
2. Ottieni Device ID, Local Key e IP:
   - Esegui il comando:
     ```bash
     python -m tinytuya scan
     ```
   - Annota **Device ID**, **Local Key** e **IP** per ogni presa Tuya.
   - In alternativa, usa strumenti come Tuya IoT Platform (richiede account sviluppatore).
3. Assicurati che la presa sia sulla stessa rete WiFi del computer (solo 2.4 GHz).

**Nota**: Se non usi prese smart, puoi saltare questa configurazione. Lo script funzionerà comunque per il monitoraggio dei miner.

## Passo 5: Preparare lo script

1. Scarica o copia lo script `axeos_monitor.py` nella directory del progetto (`axeos_monitor`).
2. Assicurati di avere:
   - Il **token** del bot Telegram (ottenuto da BotFather).
   - Il **chat ID** Telegram (invia un messaggio al bot e usa un servizio come `@GetIDsBot` per ottenerlo).
   - L'**URL API** del miner (es. `http://192.168.1.3/api/system/info`).
   - (Opzionale) I dettagli delle prese smart (Meross, Sonoff o Tuya).

## Passo 6: Avviare lo script

1. Assicurati di essere nella directory del progetto e che l'ambiente virtuale sia attivato (se usato).
2. Esegui lo script:
   - Windows:
     ```bash
     python axeos_monitor_v1.py
     ```
   - macOS/Linux:
     ```bash
     python3 axeos_monitor_v1.py
     ```

3. **Configurazione iniziale**:
   - Se il file `config.py` non esiste, lo script avvierà un wizard di configurazione.
   - Inserisci:
     - Token del bot Telegram.
     - Chat ID Telegram.
     - Soglie di temperatura (allerta e critica), durata per l'avviso critico e timeout cache.
     - Dettagli di ogni miner (nome, URL API).
     - (Opzionale) Dettagli delle prese smart (Meross: email, password, nome; Sonoff: IP, token; Tuya: Device ID, Local Key, IP).
   - Il wizard salverà la configurazione in `config.py`.

4. **Interazione con il bot**:
   - Apri Telegram e invia il comando `/start` al tuo bot.
   - Seleziona un miner dall'elenco.
   - Usa i pulsanti per visualizzare hashrate, temperatura, frequenza, stato della presa, ecc.
   - Ricevi notifiche automatiche per temperature alte/critiche o miner offline.

## Passo 7: Sicurezza

- **Proteggi `config.py`**: Il file contiene dati sensibili (token Telegram, credenziali Meross, Local Key Tuya). Non condividerlo pubblicamente e limita l'accesso al file.
- **Alternativa**: Usa variabili d'ambiente invece di `config.py`. Modifica lo script per leggere i dati con `os.getenv`:
  ```python
  import os
  TOKEN = os.getenv("TELEGRAM_TOKEN")
  CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
  ```
  Imposta le variabili d'ambiente nel tuo sistema o in un file `.env` con la libreria `python-decouple`.

## Risoluzione dei problemi

- **Errore `ModuleNotFoundError`**:
  - Assicurati che tutte le dipendenze siano installate (`pip install -r requirements.txt`).
  - Verifica di essere nell'ambiente virtuale corretto.
- **Problemi con le prese smart**:
  - **Meross**: Controlla che il nome della presa corrisponda esattamente a quello nell'app Meross. Verifica email e password.
  - **Sonoff**: Assicurati che l'IP sia corretto e che il dispositivo sia in modalità DIY o accessibile localmente.
  - **Tuya**: Riconferma Device ID, Local Key e IP con `tinytuya scan`. Assicurati che il dispositivo sia sulla rete locale.
- **Bot non risponde**:
  - Verifica che il token e il chat ID siano corretti.
  - Controlla la connessione Internet e i log dello script per errori.
- **API del miner non raggiungibile**:
  - Assicurati che l'URL API sia corretto e che il miner sia sulla stessa rete del computer.

## Supporto

Se incontri problemi o hai bisogno di aiuto:
- Controlla i log dello script (visualizzati nel terminale).
- Consulta la documentazione delle librerie:
  - [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
  - [meross-iot](https://github.com/albertogeniola/MerossIot)
  - [tinytuya](https://github.com/jasonacox/tinytuya)
- Contatta lo sviluppatore (@PakyITA) tramite Telegram con riferimento a AxeOs Monitor.

**Donazioni**:
- Supporta lo sviluppo:
  - ₿ Bitcoin: `bc1qd5fjjw7ljpyw7p8km66zqpmry6l4j2ggmu33vu`
  - 🪙 BKC: `BEPpDxbyopwoDrXLdMt8UHaTvD4f1tjEfT`

**Creato e ideato da PakyITA** 👨‍💻
