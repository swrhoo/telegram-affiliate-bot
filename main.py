import os, re, requests
from telethon import TelegramClient, events
from telegram import Bot

# Leggi le variabili d’ambiente
API_ID    = int(os.getenv('TELEGRAM_API_ID'))
API_HASH  = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SOURCE    = '@DigitalOfferte'
DEST      = '@scontiweb1'
TAG       = 'salchi-21'

# Trova ASIN e costruisci link affiliazione
def extract_asin(url):
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    if m: return m.group(1)
    r = requests.get(url, allow_redirects=True)
    return extract_asin(r.url)

def to_affiliate(url):
    asin = extract_asin(url)
    return f'https://www.amazon.it/dp/{asin}/?tag={TAG}' if asin else url

# Avvia client Telegram
client = TelegramClient('session', API_ID, API_HASH)
bot = Bot(token=BOT_TOKEN)

@client.on(events.NewMessage(chats=SOURCE))
async def handler(ev):
    text = ev.raw_text
    for link in re.findall(r'https?://\S+', text):
        if 'amzn.to' in link or '/dp/' in link:
            text = text.replace(link, to_affiliate(link))
    bot.send_message(chat_id=DEST, text=text)

client.start()
client.run_until_disconnected()
