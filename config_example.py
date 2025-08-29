# --- Telegram ---
TOKEN = "INSERISCI_IL_TUO_TOKEN"
CHAT_ID = "INSERISCI_IL_TUO_CHAT_ID"

# --- Miner ---
MINERS = [
    {
        "name": "NomeMiner",
        "local_api_url": "http://192.168.1.x/api/system/info",
        "smart_plug": None  # Oppure {"type": "meross", "email": "", "password": "", "name": ""}
    }
]

# --- Monitoraggio temperatura ---
TEMP_THRESHOLD = 70
TEMP_CRITICAL = 75
TEMP_DURATION = 10
CACHE_TIMEOUT = 5
