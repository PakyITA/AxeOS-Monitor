import time
import logging
import requests
import asyncio
import os
import signal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import tinytuya

CONFIG_FILE = "config.py"

# --- Wizard di configurazione ---
def create_config():
    print(r"""
\______   \_____  |  | _____.__.|   \__    ___/  _  \  
 |     ___/\__  \ |  |/ <   |  ||   | |    | /  /_\  \ 
 |    |     / __ \|    < \___  ||   | |    |/    |    \
 |____|    (____  /__|_ \/ ____||___| |____|\____|__  /
                \/     \/\/                         \/  
""")
    print("⚙️ Configurazione iniziale AxeOS Monitor")
    print("\n🙏 Supporta lo sviluppo con una donazione:")
    print("   ₿ Bitcoin: bc1qd5fjjw7ljpyw7p8km66zqpmry6l4j2ggmu33vu")
    print("   🪙 BKC: BEPpDxbyopwoDrXLdMt8UHaTvD4f1tjEfT\n")
    print("   👨‍💻 CREATO E IDEATO DA PakyITA 👨‍💻\n")

    token = input("Inserisci il TOKEN del bot Telegram: ").strip()
    chat_id = input("Inserisci il tuo CHAT_ID Telegram: ").strip()

    temp_threshold = int(input("Inserisci la soglia temperatura di allerta (es. 70): ").strip())
    temp_critical = int(input("Inserisci la soglia temperatura critica (es. 75): ").strip())
    temp_duration = int(input("Inserisci la durata (sec) prima di avviso critico (es. 10): ").strip())
    cache_timeout = int(input("Inserisci il timeout cache dati miner (sec, es. 5): ").strip())

    miners = []
    while True:
        name = input("Nome del miner: ").strip()
        ip = input(f"IP o URL API di {name} (es. http://192.168.1.3/api/system/info): ").strip()

        use_smart_plug = input("Vuoi associare una presa smart a questo miner? (s/n): ").strip().lower()
        smart_plug = None
        if use_smart_plug == "s":
            print("Tipi di prese smart supportate: meross, sonoff, tuya")
            plug_type = input("Tipo di presa smart (meross/sonoff/tuya): ").strip().lower()
            if plug_type not in ["meross", "sonoff", "tuya"]:
                print("⚠️ Tipo di presa non supportato. Configurazione saltata.")
                continue
            if plug_type == "meross":
                print("\n⚠️ IMPORTANTE: Il nome del dispositivo Meross deve corrispondere ESATTAMENTE al nome assegnato nell'app Meross (es. 'Presa Lucky Miner LV07'). Verifica nell'app Meross prima di proseguire.\n")
                plug_email = input("Email Meross: ").strip()
                plug_password = input("Password Meross: ").strip()
                plug_name = input("Nome dispositivo Meross: ").strip()
                smart_plug = {"type": plug_type, "email": plug_email, "password": plug_password, "name": plug_name}
            elif plug_type == "sonoff":
                plug_host = input("IP/host della presa Sonoff: ").strip()
                plug_token = input("Token Sonoff: ").strip()
                smart_plug = {"type": plug_type, "host": plug_host, "token": plug_token}
            elif plug_type == "tuya":
                print("\n⚠️ IMPORTANTE: Per Tuya, devi fornire Device ID, Local Key e IP. Puoi trovarli usando 'tinytuya scan' o nell'app Tuya/Smart Life.\n")
                plug_device_id = input("Device ID Tuya: ").strip()
                plug_local_key = input("Local Key Tuya: ").strip()
                plug_ip = input("IP della presa Tuya: ").strip()
                smart_plug = {"type": plug_type, "device_id": plug_device_id, "local_key": plug_local_key, "ip": plug_ip}

        miners.append({"name": name, "local_api_url": ip, "smart_plug": smart_plug})

        another = input("Vuoi aggiungere un altro miner? (s/n): ").strip().lower()
        if another != "s":
            break

    with open(CONFIG_FILE, "w") as f:
        f.write(f'# --- Telegram ---\n')
        f.write(f'TOKEN = "{token}"\n')
        f.write(f'CHAT_ID = "{chat_id}"\n\n')
        f.write(f'# --- Miner ---\n')
        f.write(f'MINERS = {repr(miners)}\n\n')
        f.write(f'# --- Monitoraggio temperatura ---\n')
        f.write(f'TEMP_THRESHOLD = {temp_threshold}\n')
        f.write(f'TEMP_CRITICAL = {temp_critical}\n')
        f.write(f'TEMP_DURATION = {temp_duration}\n')
        f.write(f'CACHE_TIMEOUT = {cache_timeout}\n\n')

    print(f"\n✅ Configurazione salvata in {CONFIG_FILE}")

if not os.path.exists(CONFIG_FILE):
    create_config()

from config import TOKEN, CHAT_ID, TEMP_THRESHOLD, TEMP_CRITICAL, TEMP_DURATION, CACHE_TIMEOUT, MINERS

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SELECT_MINER, DELETE_MINER = range(2)
miner_cache = {miner["name"]: {"data": {}, "last_cache": 0, "overheat_start": None, "offline_alert_sent": False} for miner in MINERS}

# --- Funzioni di utilità ---
def safe_float_conversion(text):
    try:
        cleaned_text = ''.join(filter(lambda x: x.isdigit() or x == '.', str(text)))
        return float(cleaned_text)
    except:
        return 0.0

def get_cached_miner_data(miner, retries=3):
    name = miner["name"]
    cache = miner_cache[name]
    current_time = time.time()

    if current_time - cache["last_cache"] < CACHE_TIMEOUT and cache["data"]:
        return cache["data"]

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(miner["local_api_url"], timeout=10)
            response.raise_for_status()
            data = response.json()
            cache["data"] = data
            cache["last_cache"] = current_time
            return data
        except Exception as e:
            logger.warning(f"⚠️ Tentativo {attempt}/{retries} fallito per miner {name}: {e}")
            time.sleep(1)

    return cache["data"] if cache["data"] else {}

def format_hashrate(value):
    return f"{value/1000:.2f} TH/s" if value >= 1000 else f"{value:.2f} GH/s"

def format_temperature(value):
    return f"{value:.1f}°C"

def format_frequency(value):
    return f"{value:.0f} MHz"

def format_voltage(value):
    return f"{value:.0f} mV"

def format_pool(data):
    url = data.get('stratumURL')
    port = data.get('stratumPort')
    if url and port:
        return f"🏊 Pool: {url}:{port}"
    elif url:
        return f"🏊 Pool: {url}:Sconosciuto"
    elif port:
        return f"🏊 Pool: Sconosciuto:{port}"
    else:
        return "🏊 Pool: Sconosciuto"

# --- Controllo prese smart ---
async def control_smart_plug(smart_plug, turn_on: bool, get_status: bool = False) -> tuple[bool, str]:
    if not smart_plug:
        logger.error("Nessuna configurazione smart plug disponibile")
        return False, "Nessuna configurazione smart plug disponibile"

    try:
        async with asyncio.timeout(10):  # Timeout di 10 secondi
            if smart_plug["type"] == "meross":
                logger.info(f"Tentativo di controllo della presa Meross: {smart_plug['name']}")
                client = await MerossHttpClient.async_from_user_password(
                    email=smart_plug["email"],
                    password=smart_plug["password"],
                    api_base_url="https://iotx-eu.meross.com"
                )
                logger.info("Connessione al client Meross riuscita")

                manager = MerossManager(http_client=client)
                await manager.async_init()
                logger.info("Inizializzazione manager completata")
                await asyncio.wait_for(manager.async_device_discovery(), timeout=20.0)
                devices = manager.find_devices()
                logger.info(f"Dispositivi trovati: {[f'{d.name} (Tipo: {d.type})' for d in devices]}")

                device = next((d for d in devices if d.name == smart_plug["name"]), None)
                if not device:
                    logger.error(f"Nessuna presa trovata con il nome {smart_plug['name']}")
                    await client.async_logout()
                    return False, f"Nessuna presa trovata con il nome {smart_plug['name']}"

                logger.info(f"Presa trovata: {device.name}")
                await device.async_update()
                logger.info(f"Presa {device.name} aggiornata con successo")

                if get_status:
                    try:
                        is_on = device.is_on
                        status_text = "✅ Accesa" if is_on else "⚡ Spenta"
                        await client.async_logout()
                        return True, status_text
                    except AttributeError:
                        logger.error(f"Proprietà is_on non supportata per {device.name}")
                        await client.async_logout()
                        return False, "Impossibile ottenere lo stato della presa"

                if turn_on:
                    await device.async_turn_on()
                    logger.info(f"Presa {device.name} accesa")
                else:
                    await device.async_turn_off()
                    logger.info(f"Presa {device.name} spenta")

                await client.async_logout()
                logger.info("Logout Meross completato")
                return True, "Operazione completata con successo"

            elif smart_plug["type"] == "sonoff":
                headers = {"Authorization": f"Bearer {smart_plug.get('token','')}"}
                r = requests.get(f"http://{smart_plug['host']}/cm?cmnd=Power%20{'On' if turn_on else 'Off'}", headers=headers, timeout=5)
                logger.info(f"Risposta Sonoff: {r.status_code}")
                if get_status:
                    r = requests.get(f"http://{smart_plug['host']}/cm?cmnd=Power", headers=headers, timeout=5)
                    if r.status_code == 200:
                        status = r.json().get("POWER", "UNKNOWN")
                        status_text = "✅ Accesa" if status == "ON" else "⚡ Spenta"
                        return True, status_text
                    return False, "Errore nel controllo dello stato della presa Sonoff"
                return r.status_code == 200, "Operazione completata con successo" if r.status_code == 200 else "Errore nel controllo della presa Sonoff"

            elif smart_plug["type"] == "tuya":
                logger.info(f"Tentativo di controllo della presa Tuya: {smart_plug['device_id']}")
                device = tinytuya.OutletDevice(
                    dev_id=smart_plug["device_id"],
                    address=smart_plug["ip"],
                    local_key=smart_plug["local_key"],
                    version=3.3
                )
                if get_status:
                    try:
                        status = device.status()
                        is_on = status.get("dps", {}).get("1", False)
                        status_text = "✅ Accesa" if is_on else "⚡ Spenta"
                        return True, status_text
                    except Exception as e:
                        logger.error(f"Errore nel controllo dello stato della presa Tuya: {e}")
                        return False, f"Errore nel controllo dello stato: {e}"
                
                try:
                    if turn_on:
                        device.turn_on()
                        logger.info(f"Presa Tuya {smart_plug['device_id']} accesa")
                    else:
                        device.turn_off()
                        logger.info(f"Presa Tuya {smart_plug['device_id']} spenta")
                    return True, "Operazione completata con successo"
                except Exception as e:
                    logger.error(f"Errore nel controllo della presa Tuya: {e}")
                    return False, f"Errore: {e}"

            else:
                logger.error(f"Tipo di presa non supportato: {smart_plug['type']}")
                return False, f"Tipo di presa non supportato: {smart_plug['type']}"
    except asyncio.TimeoutError:
        logger.error(f"Timeout durante il controllo della presa {smart_plug.get('name', smart_plug.get('device_id', ''))}")
        return False, "Timeout durante il controllo della presa"
    except Exception as e:
        logger.error(f"Errore nel controllo della presa: {e}")
        return False, f"Errore: {e}"

# --- Tastiera bot ---
def main_keyboard(miner=None):
    buttons = [
        [InlineKeyboardButton("📊 Hashrate", callback_data='hash')],
        [InlineKeyboardButton("🌡️ Temperatura", callback_data='temp')],
        [InlineKeyboardButton("⚙️ Frequenza", callback_data='frequency')],
        [InlineKeyboardButton("⚡ Core Voltage", callback_data='core')],
        [InlineKeyboardButton("🏊 Pool", callback_data='pool')],
        [InlineKeyboardButton("💰 Mined", callback_data='mined')],
        [InlineKeyboardButton("🗑️ Cancella miner", callback_data='delete')],
        [InlineKeyboardButton("📋 Status completo", callback_data='status')],
        [InlineKeyboardButton("💵 Donazione", callback_data='donate')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='back')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    if miner and miner.get("smart_plug"):
        buttons.insert(0, [
            InlineKeyboardButton("🟢 On", callback_data='turn_on'),
            InlineKeyboardButton("🔴 Off", callback_data='turn_off'),
            InlineKeyboardButton("📊 Stato", callback_data='plug_status')
        ])
    return InlineKeyboardMarkup(buttons)

# --- Handlers bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(m["name"], callback_data=f"select_{m['name']}")] for m in MINERS]
    await update.message.reply_text("Seleziona un miner:", reply_markup=InlineKeyboardMarkup(buttons))
    return SELECT_MINER

async def select_miner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    miner_name = query.data.replace("select_", "")
    context.user_data["selected_miner"] = miner_name
    miner = next((m for m in MINERS if m["name"] == miner_name), None)
    await query.edit_message_text(f"Miner selezionato: {miner_name}", reply_markup=main_keyboard(miner))
    return ConversationHandler.END

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MINERS
    query = update.callback_query
    await query.answer()
    miner_name = context.user_data.get("selected_miner")
    miner = next((m for m in MINERS if m["name"] == miner_name), None)
    data = get_cached_miner_data(miner) if miner else {}

    if query.data == "back":
        buttons = [[InlineKeyboardButton(m["name"], callback_data=f"select_{m['name']}")] for m in MINERS]
        await query.edit_message_text("Seleziona un miner:", reply_markup=InlineKeyboardMarkup(buttons))
        return SELECT_MINER

    if miner:
        if query.data == "turn_on":
            success, message = await control_smart_plug(miner.get("smart_plug"), True)
            await query.edit_message_text(f"✅ Miner acceso." if success else f"⚠️ Errore nell'accensione: {message}", reply_markup=main_keyboard(miner))
            return
        if query.data == "turn_off":
            success, message = await control_smart_plug(miner.get("smart_plug"), False)
            await query.edit_message_text(f"✅ Miner spento." if success else f"⚠️ Errore nello spegnimento: {message}", reply_markup=main_keyboard(miner))
            return
        if query.data == "plug_status":
            success, message = await control_smart_plug(miner.get("smart_plug"), False, get_status=True)
            await query.edit_message_text(f"Stato presa: {message}" if success else f"⚠️ Errore nel controllo dello stato: {message}", reply_markup=main_keyboard(miner))
            return
        if query.data == "delete":
            buttons = [[InlineKeyboardButton(m["name"], callback_data=f"delete_{m['name']}")] for m in MINERS]
            await query.edit_message_text("Seleziona il miner da cancellare:", reply_markup=InlineKeyboardMarkup(buttons))
            return DELETE_MINER
        if query.data.startswith("delete_"):
            mname = query.data.replace("delete_", "")
            MINERS = [m for m in MINERS if m["name"] != mname]
            with open(CONFIG_FILE, "w") as f:
                f.write(f'# --- Telegram ---\nTOKEN="{TOKEN}"\nCHAT_ID="{CHAT_ID}"\n\n')
                f.write(f'# --- Miner ---\nMINERS={repr(MINERS)}\n\n')
                f.write(f'# --- Monitoraggio temperatura ---\nTEMP_THRESHOLD={TEMP_THRESHOLD}\nTEMP_CRITICAL={TEMP_CRITICAL}\nTEMP_DURATION={TEMP_DURATION}\nCACHE_TIMEOUT={CACHE_TIMEOUT}\n\n')
            await query.edit_message_text(f"🗑️ Miner {mname} cancellato.", reply_markup=main_keyboard())
            return ConversationHandler.END

    if query.data == "donate":
        msg = ("🙏 Supporta lo sviluppo:\n₿ Bitcoin: bc1qd5fjjw7ljpyw7p8km66zqpmry6l4j2ggmu33vu\n"
               "🪙 BKC: BEPpDxbyopwoDrXLdMt8UHaTvD4f1tjEfT\n👨‍💻 CREATO E IDEATO DA PakyITA 👨‍💻")
        await query.edit_message_text(msg, reply_markup=main_keyboard(miner))
        return

    responses = {
        'hash': lambda: f"📊 Hashrate: {format_hashrate(data.get('hashRate', 0))}",
        'temp': lambda: f"🌡️ Temperatura: {format_temperature(data.get('temp', 0))}",
        'frequency': lambda: f"⚙️ Frequenza: {format_frequency(data.get('frequency', 0))}",
        'core': lambda: f"⚡ Core Voltage: {format_voltage(data.get('coreVoltageActual', 0))}",
        'pool': lambda: format_pool(data),
        'mined': lambda: "💰 Funzione in sviluppo...",
        'status': lambda: "\n".join(f"{k}: {v}" for k, v in data.items()),
        'help': lambda: ("ℹ️ Comandi:\n📊 Hashrate\n🌡️ Temperatura\n⚙️ Frequenza\n⚡ Core Voltage\n"
                        "🏊 Pool\n💰 Mined\n📋 Status completo\n📊 Stato\n❓ Help\n⬅️ Indietro\n🔛 On\n🔴 Off\n💵 Donazione")
    }

    func = responses.get(query.data)
    if func:
        await query.edit_message_text(func(), reply_markup=main_keyboard(miner))

# --- Monitoraggio temperature ---
async def monitor_miners(app):
    while True:
        try:
            for miner in MINERS:
                name = miner["name"]
                cache = miner_cache[name]
                data = get_cached_miner_data(miner)
                if not data:
                    if CHAT_ID and not cache["offline_alert_sent"]:
                        await app.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Miner {name} offline o API non raggiungibile!")
                        cache["offline_alert_sent"] = True
                    continue
                else:
                    cache["offline_alert_sent"] = False

                temp = safe_float_conversion(data.get('temp', 0))
                if temp > TEMP_THRESHOLD:
                    if cache["overheat_start"] is None:
                        cache["overheat_start"] = time.time()
                    elif time.time() - cache["overheat_start"] >= TEMP_DURATION:
                        if CHAT_ID:
                            await app.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Miner {name} temperatura alta: {temp:.1f}°C")
                        cache["overheat_start"] = None
                else:
                    cache["overheat_start"] = None

                if temp >= TEMP_CRITICAL:
                    if CHAT_ID:
                        await app.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Miner {name} temperatura critica {temp:.1f}°C!")
                    if miner.get("smart_plug"):
                        success, message = await control_smart_plug(miner.get("smart_plug"), False)
                        if not success:
                            logger.error(f"Errore nello spegnimento della presa per temperatura critica: {message}")

            await asyncio.sleep(300)
        except asyncio.CancelledError:
            logger.info("monitor_miners annullato")
            raise
        except Exception as e:
            logger.error(f"Errore in monitor_miners: {e}")
            await asyncio.sleep(300)  # Continua dopo un errore

# --- Gestione dell'interruzione ---
async def shutdown(application):
    logger.info("Inizio processo di shutdown")
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    logger.info(f"Task da annullare: {[task.get_name() for task in tasks]}")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    
    for miner in MINERS:
        if miner.get("smart_plug") and miner["smart_plug"]["type"] in ["meross", "sonoff", "tuya"]:
            success, message = await control_smart_plug(miner.get("smart_plug"), False)
            if not success:
                logger.error(f"Errore durante il logout per {miner['name']}: {message}")

    if application.running:
        logger.info("Arresto dell'applicazione")
        await application.stop()
        logger.info("Chiusura dell'applicazione")
        await application.shutdown()
        logger.info("Bot chiuso correttamente")
    else:
        logger.info("Applicazione già arrestata")

def handle_shutdown(application):
    asyncio.create_task(shutdown(application))

# --- Main ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_MINER: [CallbackQueryHandler(select_miner)],
            DELETE_MINER: [CallbackQueryHandler(button)]
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button))

    async def post_init(app_instance):
        asyncio.create_task(monitor_miners(app_instance))
        logger.info("✅ Bot avviato e monitoraggio attivo.")

    app.post_init = post_init

    def signal_handler(sig, frame):
        logger.info(f"Segnale {sig} ricevuto, chiusura del bot...")
        handle_shutdown(app)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal_handler)

    try:
        print("\n⚡ AxeOS Monitor v1.1 by PakyITA ⚡")
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Interruzione ricevuta, chiusura del bot...")
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione del bot: {e}")

if __name__ == "__main__":
    main()
