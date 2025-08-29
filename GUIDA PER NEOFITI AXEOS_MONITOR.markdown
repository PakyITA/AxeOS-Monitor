# Guida per Neofiti: Come Usare AxeOS Monitor

**AxeOS Monitor** è un programma che ti permette di controllare i tuoi miner di criptovalute tramite Telegram. Puoi vedere dati come temperatura e hashrate, e (se vuoi) accendere o spegnere i miner usando prese smart come Meross, Sonoff o Tuya. Questa guida è pensata per chi non ha molta esperienza con i computer. Seguila passo-passo e non preoccuparti, è più semplice di quanto sembri!

## Cosa ti serve prima di iniziare

- Un computer (Windows, Mac o Linux) con connessione a Internet.
- Un **bot Telegram**:
  - Crea un bot usando l’app Telegram e il contatto **@BotFather**. Ti darà un **token** (una stringa di lettere e numeri).
  - Scopri il tuo **chat ID** (il tuo ID su Telegram) usando un bot come **@GetIDsBot**.
- L’**indirizzo del miner** (es. `http://192.168.1.3/api/system/info`). Di solito lo trovi nel manuale o nell’interfaccia web del miner.
- (Opzionale) Una presa smart Meross, Sonoff o Tuya configurata con l’app del produttore.
- Un po’ di pazienza! 😊

Se non usi prese smart, puoi comunque usare il bot per controllare i tuoi miner.

## Passo 1: Installare Python

Python è il programma che fa funzionare lo script. Devi installarlo sul tuo computer.

### Su Windows
1. Vai al sito [python.org](https://www.python.org/downloads/) usando il browser.
2. Scarica l’ultima versione di Python (es. Python 3.11 o 3.12).
3. Apri il file scaricato e segui questi passi:
   - Spunta la casella **“Add Python to PATH”** (molto importante!).
   - Clicca su **“Install Now”**.
4. Per controllare che Python sia installato:
   - Apri il **Prompt dei comandi** (scrivi `cmd` nella barra di ricerca di Windows e premi Invio).
   - Digita:
     ```bash
     python --version
     ```
   - Se vedi qualcosa come `Python 3.11.4`, hai fatto tutto giusto!

### Su Mac
1. Apri il **Terminale** (lo trovi cercando “Terminale” nel Launchpad).
2. Controlla se Python è già installato:
   ```bash
   python3 --version
   ```
3. Se non c’è o la versione è vecchia (inferiore a 3.8), scarica Python da [python.org](https://www.python.org/downloads/) e installalo.
   - In alternativa, se hai Homebrew (un programma per gestire software su Mac), digita:
     ```bash
     brew install python3
     ```
     Si consiglia vivamente di installare python 3.11
     
4. Verifica l’installazione:
   ```bash
   python3 --version
   ```

### Su Linux (es. Ubuntu)
1. Apri il **Terminale** (di solito lo trovi nel menu delle applicazioni).
2. Aggiorna il sistema:
   ```bash
   sudo apt update
   ```
3. Installa Python:
   ```bash
   sudo apt install python3 python3-pip
   ```
4. Verifica l’installazione:
   ```bash
   python3 --version
   ```

## Passo 2: Preparare una cartella per il progetto

1. Crea una cartella chiamata `axeos_monitor` sul tuo computer:
   - Windows: Crea una cartella sul Desktop o in Documenti.
   - Mac/Linux: Apri il Terminale e digita:
     ```bash
     mkdir axeos_monitor
     cd axeos_monitor
     ```

2. Scarica o copia lo script `axeos_monitor.py` in questa cartella. Puoi:
   - Copiarlo da un sito o email.
   - Chiedere allo sviluppatore (PakyITA) di fornirtelo.
  
Attivare l'ambiente virtuale:
Da terminale:
```
python3.11 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```
Da terminale esegui:
```
pip install --upgrade pip wheel setuptools #Se il primo comando non funziona prova questo>>> pip install --upgrade pip wheel setuptools
```

## Passo 3: Installare i programmi necessari (dipendenze)

Lo script ha bisogno di alcune “librerie” per funzionare, come pezzi di un puzzle. Le installiamo con un file chiamato `requirements.txt`.


1. Crea un file chiamato `requirements.txt` nella cartella `axeos_monitor`. Aprilo con un editor di testo (es. Blocco Note su Windows, TextEdit su Mac) e incolla questo testo:
   ```
   python-telegram-bot==20.3
   requests==2.31.0
   meross-iot==1.3.2
   tinytuya==1.15.0
   ```

2. Apri il terminale (Prompt dei comandi su Windows, Terminale su Mac/Linux) e vai nella cartella `axeos_monitor`:
   - Windows:
     ```bash
     cd Desktop\axeos_monitor
     ```
   - Mac/Linux:
     ```bash
     cd ~/axeos_monitor
     ```

3. Installa le librerie:
   - Windows:
     ```bash
     pip install -r requirements.txt
     ```
   - Mac/Linux:
     ```bash
     pip3 install -r requirements.txt
     ```

4. Se tutto va bene, non vedrai errori. Per sicurezza, controlla le librerie installate:
   ```bash
   pip list
   ```
   Cerca `python-telegram-bot`, `requests`, `meross-iot` e `tinytuya`.

### Se qualcosa va storto
- **Errore “pip not found”**:
  - Usa `python -m pip` (Windows) o `python3 -m pip` (Mac/Linux) invece di `pip` o `pip3`.
- **Problemi di rete**:
  - Aggiungi questo al comando:
    ```bash
    pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
    ```

## Passo 4: Configurare le prese smart (opzionale)

Se non usi prese smart, salta questo passaggio. Il bot funzionerà lo stesso per controllare i miner.

### Meross
1. Scarica l’app **Meross** (App Store/Play Store).
2. Configura la presa smart seguendo le istruzioni dell’app (connettila alla rete WiFi, solo 2.4 GHz).
3. Annota:
   - La tua **email** e **password** di Meross.
   - Il **nome** della presa (es. “Presa Miner 1”), che deve essere ESATTAMENTE come appare nell’app.

### Sonoff
1. Scarica l’app **eWeLink** (App Store/Play Store).
2. Configura la presa smart seguendo le istruzioni (connettila alla rete WiFi, solo 2.4 GHz).
3. Trova l’**IP** della presa:
   - Controlla nel tuo router (cerca l’elenco dei dispositivi connessi).
   - O usa un’app come **Fing** per scansionare la rete.
4. Annota il **token** (se usi eWeLink o un firmware come Tasmota, lo trovi nell’app o nell’interfaccia web).

### Tuya
1. Scarica l’app **Tuya Smart** o **Smart Life** (App Store/Play Store).
2. Configura la presa smart (connettila alla rete WiFi, solo 2.4 GHz).
3. Trova **Device ID**, **Local Key** e **IP**:
   - Apri il terminale nella cartella `axeos_monitor` e digita:
     ```bash
     python -m tinytuya scan
     ```
   - Vedrai un elenco di dispositivi Tuya. Annota:
     - **Device ID** (una stringa lunga di lettere e numeri).
     - **Local Key** (un’altra stringa lunga).
     - **IP** (es. `192.168.1.100`).
4. Se non riesci, chiedi aiuto allo sviluppatore o cerca nella documentazione di Tuya.

## Passo 5: Avviare lo script

1. Assicurati di essere nella cartella `axeos_monitor`:
   - Windows:
     ```bash
     cd Desktop\axeos_monitor
     ```
   - Mac/Linux:
     ```bash
     cd ~/axeos_monitor
     ```

2. Avvia lo script:
   - Windows:
     ```bash
     python axeos_monitor.py
     ```
   - Mac/Linux:
     ```bash
     python3 axeos_monitor.py
     ```

3. **Configura il bot**:
   - La prima volta, lo script ti chiederà di inserire:
     - Il **token** del bot Telegram.
     - Il tuo **chat ID** Telegram.
     - La **temperatura di allerta** (es. 70°C).
     - La **temperatura critica** (es. 75°C).
     - La **durata** prima di un avviso critico (es. 10 secondi).
     - Il **timeout cache** (es. 5 secondi, per aggiornare i dati del miner).
     - Per ogni miner:
       - Un **nome** (es. “Miner 1”).
       - L’**URL API** (es. `http://192.168.1.3/api/system/info`).
       - (Opzionale) I dettagli della presa smart (Meross, Sonoff o Tuya).
   - Puoi aggiungere più miner rispondendo “s” alla domanda “Vuoi aggiungere un altro miner?”.
   - Alla fine, lo script crea un file `config.py` con tutte le informazioni.

4. **Usa il bot su Telegram**:
   - Apri Telegram e cerca il tuo bot.
   - Invia il comando `/start`.
   - Scegli un miner dalla lista.
   - Usa i pulsanti per:
     - Vedere hashrate, temperatura, frequenza, ecc.
     - Accendere/spegnere la presa smart (se configurata).
     - Controllare lo stato della presa.
   - Riceverai messaggi automatici se il miner è offline o se la temperatura è troppo alta.

## Passo 6: Proteggi i tuoi dati

- Il file `config.py` contiene informazioni importanti (es. token Telegram, password Meross). Non condividerlo con nessuno!
- Metti il file in una cartella sicura o chiedi allo sviluppatore come usare variabili d’ambiente per maggiore sicurezza.

## Cosa fare se qualcosa non funziona

- **Lo script non parte**:
  - Controlla che Python sia installato (`python --version` o `python3 --version`).
  - Assicurati che tutte le librerie siano installate (`pip list`).
- **Il bot non risponde su Telegram**:
  - Verifica che il token e il chat ID siano corretti.
  - Controlla di avere Internet.
- **Problemi con le prese smart**:
  - **Meross**: Assicurati che il nome della presa sia ESATTAMENTE quello dell’app Meross.
  - **Sonoff**: Controlla che l’IP sia giusto e che la presa sia accesa.
  - **Tuya**: Riprova con `python -m tinytuya scan` per confermare Device ID, Local Key e IP.
- **Il miner non risponde**:
  - Controlla che l’URL API sia corretto e che il miner sia acceso e sulla stessa rete WiFi.

Se hai problemi, chiedi aiuto allo sviluppatore (PakyITA) o controlla i messaggi di errore nel terminale.

## Donazioni

Se ti piace AxeOS Monitor, supporta lo sviluppatore:
- ₿ Bitcoin: `bc1qd5fjjw7ljpyw7p8km66zqpmry6l4j2ggmu33vu`
- 🪙 BKC: `BEPpDxbyopwoDrXLdMt8UHaTvD4f1tjEfT`

**Creato e ideato da PakyITA** 👨‍💻

Buon monitoraggio dei tuoi miner! 🚀
