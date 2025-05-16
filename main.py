import os
import re
import requests
from telethon import TelegramClient, events

# Leggi le variabili d’ambiente
API_ID    = int(os.getenv('TELEGRAM_API_ID'))
API_HASH  = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SOURCE    = '@DigitalOfferte'
DEST      = '@scontiweb1'
TAG       = 'salchi-21'

# Inizializza il client direttamente come bot (senza prompt interattivo)
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Trova ASIN e costruisci link affiliazione
def extract_asin(url):
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    if m:
        return m.group(1)
    # se è uno short-link, espandi e riprova
    r = requests.get(url, allow_redirects=True)
    return extract_asin(r.url)

def to_affiliate(url):
    asin = extract_asin(url)
    return f'https://www.amazon.it/dp/{asin}/?tag={TAG}' if asin else url

@client.on(events.NewMessage(chats=SOURCE))
async def handler(ev):
    text = ev.raw_text
    # sostituisci ogni link rilevante
    for link in re.findall(r'https?://\S+', text):
        if 'amzn.to' in link or '/dp/' in link:
            text = text.replace(link, to_affiliate(link))
    # inoltra il testo modificato
    await client.send_message(DEST, text)

# Avvia il bot
client.run_until_disconnected()
