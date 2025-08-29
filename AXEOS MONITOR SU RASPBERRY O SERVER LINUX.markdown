# Guida per Installare AxeOS Monitor su Raspberry Pi con Raspbian e Avviarlo Automaticamente

**AxeOS Monitor** è un bot Telegram che ti permette di monitorare i tuoi miner di criptovalute (es. hashrate, temperatura) e, se vuoi, controllare prese smart (Meross, Sonoff o Tuya). Questa guida ti spiega come installarlo su un **Raspberry Pi** con **Raspbian** (Raspberry Pi OS) e fare in modo che si avvii da solo ogni volta che accendi il Raspberry Pi. È pensata per chi non ha molta esperienza, quindi segui i passaggi uno per uno!

## Cosa ti serve

- Un **Raspberry Pi** (es. Pi 3, 4 o 5) con **Raspbian** installato (usa l'ultima versione, come Raspberry Pi OS basato su Debian 12).
- Connessione a Internet (WiFi o Ethernet).
- Accesso al Raspberry Pi:
  - Con monitor, tastiera e mouse.
  - O tramite **SSH** da un altro computer (attiva SSH da `raspi-config`).
- Il file `axeos_monitor_v1.py` (scaricalo o copialo nella guida).
- Un **bot Telegram**:
  - Crea un bot con **@BotFather** su Telegram per ottenere il **token**.
  - Trova il tuo **chat ID** con un bot come **@GetIDsBot**.
- L'**URL API** del tuo miner (es. `http://192.168.1.3/api/system/info`, lo trovi nel manuale o interfaccia web del miner).
- (Opzionale) Una presa smart Meross, Sonoff o Tuya configurata con l’app del produttore.

**Nota**: Se non usi prese smart, il bot funziona lo stesso per monitorare i miner.

---

## Passo 1: Aggiorna Raspbian e Installa Python

Python è già presente su Raspbian, ma dobbiamo assicurarci che sia aggiornato.

1. Apri il **Terminale** sul Raspberry Pi (lo trovi nel menu o usa SSH).
2. Aggiorna il sistema:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
   Inserisci la password (di default è `raspberry`) e attendi il completamento.

3. Installa Python 3 e pip (se non sono già presenti):
   ```bash
   sudo apt install python3 python3-pip -y
   ```

4. Verifica l’installazione:
   ```bash
   python3 --version
   pip3 --version
   ```
   Dovresti vedere qualcosa come `Python 3.11.x` e `pip 23.x`. Se tutto è ok, vai avanti!

---

## Passo 2: Prepara la Cartella e Installa le Dipendenze

1. Crea una cartella per il progetto:
   ```bash
   mkdir ~/axeos_monitor_v1
   cd ~/axeos_monitor_v1
   ```

2. Copia lo script `axeos_monitor_v1.py` nella cartella `axeos_monitor_v1`:
   - Se lo hai su una chiavetta USB:
     - Collega la chiavetta al Raspberry Pi.
     - Trova la chiavetta (es. in `/media/pi/USB`):
       ```bash
       ls /media/pi
       ```
     - Copia il file:
       ```bash
       cp /media/pi/USB/axeos_monitor_v1.py .
       ```
   - Oppure, scaricalo con il browser del Raspberry Pi o usa `wget` se hai un link diretto:
     ```bash
     wget URL_DEL_TUO_SCRIPT
     ```

3. Crea un file `requirements.txt`:
   ```bash
   nano requirements.txt
   ```
   Incolla questo testo e salva (Ctrl+O, Invio, Ctrl+X):
   ```
   python-telegram-bot==20.3
   requests==2.31.0
   meross-iot==1.3.2
   tinytuya==1.15.0
   ```

4. Installa le dipendenze:
   ```bash
   pip3 install -r requirements.txt
   ```

5. Verifica che le librerie siano installate:
   ```bash
   pip3 list
   ```
   Cerca `python-telegram-bot`, `requests`, `meross-iot` e `tinytuya` nell’elenco.

**Se qualcosa va storto**:
- **Errore “pip not found”**: Usa `python3 -m pip` invece di `pip3`.
- **Problemi di rete**: Aggiungi `--trusted-host pypi.org --trusted-host files.pythonhosted.org` al comando `pip3 install`.

---

## Passo 3: Configura lo Script

1. Avvia lo script per la prima configurazione:
   ```bash
   python3 axeos_monitor_v1.py
   ```

2. Segui il wizard che appare nel terminale:
   - Inserisci il **token** del bot Telegram (da @BotFather).
   - Inserisci il tuo **chat ID** Telegram (da @GetIDsBot).
   - Scegli la **temperatura di allerta** (es. 70°C), **temperatura critica** (es. 75°C), **durata avviso critico** (es. 10 secondi) e **timeout cache** (es. 5 secondi).
   - Per ogni miner:
     - Dai un **nome** (es. “Miner 1”).
     - Inserisci l’**URL API** (es. `http://192.168.1.3/api/system/info`).
     - (Opzionale) Configura una presa smart:
       - **Meross**: Email, password e nome esatto della presa (dall’app Meross).
       - **Sonoff**: IP della presa (trovalo nel router) e token (da eWeLink o Tasmota).
       - **Tuya**: Device ID, Local Key e IP (usa `python3 -m tinytuya scan` per trovarli).
   - Aggiungi altri miner rispondendo “s” o termina con “n”.

3. Il wizard crea un file `config.py` nella cartella `axeos_monitor_v1`.

4. Testa il bot:
   - Apri Telegram, cerca il tuo bot e invia `/start`.
   - Scegli un miner e prova i pulsanti (es. per vedere hashrate o accendere una presa).
   - Verifica che ricevi notifiche per temperature alte o miner offline.

5. Ferma lo script con **Ctrl+C** nel terminale.

---

## Passo 4: Configura l’Avvio Automatico con Systemd

Per far partire il bot ogni volta che il Raspberry Pi si accende, usiamo **systemd**, che gestisce i programmi in background.

1. Crea un file di servizio:
   ```bash
   sudo nano /etc/systemd/system/axeos_monitor_v1.service
   ```

2. Incolla questo testo (assicurati che il percorso `/home/pi/axeos_monitor_v1_v1` sia corretto - nel caso abbia usato un username differente e pi es. marco allora il percorso sarà `/home/marco/axeos_monitor_v1_v1`):
   ```
   [Unit]
   Description=AxeOS Monitor Service
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/axeos_monitor_v1
   ExecStart=/usr/bin/python3 /home/pi/axeos_monitor_v1/axeos_monitor_v1.py
   Restart=always
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```
   - **Spiegazione**:
     - `User=pi`: Esegue il servizio come utente `pi` (il default su Raspbian).
     - `WorkingDirectory`: La cartella dello script.
     - `ExecStart`: Il comando per avviare lo script.
     - `Restart=always`: Riavvia il bot se si ferma.
     - `After=network.target`: Aspetta che la rete sia attiva.

   Salva (Ctrl+O, Invio, Ctrl+X).

3. Ricarica systemd e abilita il servizio:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable axeos_monitor_v1.service
   ```

4. Avvia il servizio per testarlo:
   ```bash
   sudo systemctl start axeos_monitor_v1.service
   ```

5. Controlla se funziona:
   ```bash
   sudo systemctl status axeos_monitor_v1.service
   ```
   Cerca “Active: active (running)”. Se vedi errori, guarda i log:
   ```bash
   journalctl -u axeos_monitor_v1.service -e
   ```

6. Riavvia il Raspberry Pi per verificare l’avvio automatico:
   ```bash
   sudo reboot
   ```
   Dopo il riavvio, controlla di nuovo con `sudo systemctl status axeos_monitor_v1.service`. Il bot dovrebbe essere attivo su Telegram.

---

## Passo 5: Configurare le Prese Smart (Opzionale)

Se non usi prese smart, salta questo passaggio. Il bot funziona comunque.

### Meross
- Scarica l’app **Meross** (App Store/Play Store).
- Configura la presa (connettila alla WiFi, solo 2.4 GHz).
- Annota: **email**, **password** e **nome esatto** della presa (es. “Presa Miner 1”) dall’app.

### Sonoff
- Scarica l’app **eWeLink** (App Store/Play Store).
- Configura la presa (WiFi 2.4 GHz).
- Trova l’**IP** (nel router o con un’app come Fing).
- Trova il **token** (da eWeLink o, se usi Tasmota, dall’interfaccia web).

### Tuya
- Scarica l’app **Tuya Smart** o **Smart Life** (App Store/Play Store).
- Configura la presa (WiFi 2.4 GHz).
- Trova **Device ID**, **Local Key** e **IP**:
  ```bash
  python3 -m tinytuya scan
  ```
  Annota i dettagli per ogni presa.

Inserisci questi dati nel wizard di configurazione (Passo 3).

---

## Passo 6: Gestire il Bot e Risolvere Problemi

### Gestire il Servizio
- **Ferma il bot**:
  ```bash
  sudo systemctl stop axeos_monitor_v1.service
  ```
- **Riavvia il bot** (es. dopo aver modificato `config.py`):
  ```bash
  sudo systemctl restart axeos_monitor_v1.service
  ```
- **Disabilita l’avvio automatico**:
  ```bash
  sudo systemctl disable axeos_monitor_v1.service
  ```

### Problemi Comuni
- **Il bot non parte**:
  - Controlla i log: `journalctl -u axeos_monitor_v1.service -e`.
  - Verifica che `config.py` sia nella cartella `axeos_monitor_v1`.
  - Assicurati che le dipendenze siano installate (`pip3 list`).
- **Il bot non risponde su Telegram**:
  - Controlla che il **token** e il **chat ID** in `config.py` siano corretti.
  - Verifica la connessione a Internet.
- **Problemi con le prese smart**:
  - **Meross**: Assicurati che il nome della presa sia ESATTAMENTE quello dell’app Meross.
  - **Sonoff**: Controlla che l’IP sia corretto e la presa sia accesa.
  - **Tuya**: Riprova con `python3 -m tinytuya scan` per confermare Device ID, Local Key e IP.
- **Il miner non risponde**:
  - Verifica che l’URL API sia corretto e che il miner sia sulla stessa rete WiFi.
- **Internet lento all’avvio**:
  - Modifica il file di servizio per aggiungere un ritardo:
    ```bash
    sudo nano /etc/systemd/system/axeos_monitor_v1.service
    ```
    Cambia `ExecStart` in:
    ```
    ExecStart=/bin/bash -c 'sleep 10; /usr/bin/python3 /home/pi/axeos_monitor_v1/axeos_monitor_v1.py'
    ```
    Poi ricarica: `sudo systemctl daemon-reload`.

---

## Passo 7: Proteggi i Tuoi Dati

- Il file `config.py` contiene dati sensibili (es. token Telegram, password Meross, Local Key Tuya). Non condividerlo!
- Usa una password forte per l’utente `pi`:
  ```bash
  passwd
  ```
- Se il Raspberry Pi è accessibile da Internet, configura un firewall:
  ```bash
  sudo apt install ufw
  sudo ufw enable
  ```

---

## Donazioni

Se AxeOS Monitor ti piace, supporta lo sviluppatore:
- ₿ Bitcoin: `bc1qd5fjjw7ljpyw7p8km66zqpmry6l4j2ggmu33vu`
- 🪙 BKC: `BEPpDxbyopwoDrXLdMt8UHaTvD4f1tjEfT`

**Creato e ideato da PakyITA** 👨‍💻

Buon monitoraggio dei tuoi miner con il tuo Raspberry Pi! 🚀
