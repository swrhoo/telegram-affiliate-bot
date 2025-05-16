import os, re, requests, threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Bot
from http.server import HTTPServer, BaseHTTPRequestHandler

# Variabili d’ambiente
API_ID    = int(os.getenv('TELEGRAM_API_ID'))
API_HASH  = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SESSION   = os.getenv('SESSION_STRING')

SOURCE = '@DigitalOfferte'
DEST   = '@scontiweb1'
TAG    = 'salchi-21'
PORT   = int(os.getenv('PORT', '8000'))  # Porta per l’HTTP server

# Dummy HTTP server per soddisfare il controllo porte di Render
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_http_server():
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    server.serve_forever()

# Avvia il server in background
threading.Thread(target=start_http_server, daemon=True).start()

# Setup Telegram user-client e bot-client
user_client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
bot         = Bot(token=BOT_TOKEN)

@user_client.on(events.NewMessage(chats=SOURCE))
async def handler(ev):
    text = ev.raw_text
    for link in re.findall(r'https?://\S+', text):
        if 'amzn.to' in link or '/dp/' in link:
            dest = requests.get(link, allow_redirects=True).url
            asin = re.search(r'/dp/([A-Z0-9]{10})', dest).group(1)
            new_url = f'https://www.amazon.it/dp/{asin}/?tag={TAG}'
            text = text.replace(link, new_url)
    bot.send_message(chat_id=DEST, text=text)

if __name__ == '__main__':
    print(f"✅ Bot avviato e HTTP server in ascolto sulla porta {PORT}")
    user_client.start()
    user_client.run_until_disconnected()
