import os
import re
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Bot

# Variabili d'ambiente
API_ID    = int(os.getenv('TELEGRAM_API_ID'))
API_HASH  = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SESSION   = os.getenv('SESSION_STRING')

SOURCE = '@DigitalOfferte'
DEST   = '@scontiweb1'
TAG    = 'salchi-21'

# Setup client utente e bot
user_client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
bot         = Bot(token=BOT_TOKEN)

async def main():
    # Avvia il client utente senza prompt
    await user_client.start()
    @user_client.on(events.NewMessage(chats=SOURCE))
    async def handler(ev):
        text = ev.raw_text
        for link in re.findall(r'https?://\S+', text):
            if 'amzn.to' in link or '/dp/' in link:
                dest = requests.get(link, allow_redirects=True).url
                m = re.search(r'/dp/([A-Z0-9]{10})', dest)
                if m:
                    asin = m.group(1)
                    new_url = f'https://www.amazon.it/dp/{asin}/?tag={TAG}'
                    text = text.replace(link, new_url)
        bot.send_message(chat_id=DEST, text=text)
    print(f"✅ Bot avviato e in ascolto su {SOURCE}")
    await user_client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
