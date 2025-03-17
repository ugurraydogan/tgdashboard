from telethon import TelegramClient, events
import asyncio
import re
import os
import datetime
import json
from collections import defaultdict
import logging

# Logging ayarları herhangi bir hata alırsanız instagram @ugurayydogan
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Yapılandırma dosyası
CONFIG_FILE = 'config.json'

class TelegramMonitor:
    def __init__(self):
        self.config = self.load_config()
        self.client = None
        self.results = defaultdict(list)

    def load_config(self):
        """Yapılandırma dosyasını yükler veya varsayılan yapılandırmayı oluşturur."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = {
                'api_id': '',
                'api_hash': '',
                'phone': '',
                'keywords': ['Turkey'],
                'groups': [],
                'save_results': True,
                'results_file': 'results.json'
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            print(f"Lütfen {CONFIG_FILE} dosyasını düzenleyiniz.")
            return default_config

    def save_config(self):
        """Yapılandırmayı kaydeder."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    async def setup_client(self):
        """Telegram istemcisini ayarlar ve oturum açar."""
        if not self.config['api_id'] or not self.config['api_hash']:
            print("Lütfen config.json dosyasında api_id ve api_hash değerlerini ayarlayın.")
            return False

        session_file = f"session_{self.config['phone']}"
        self.client = TelegramClient(session_file, self.config['api_id'], self.config['api_hash'])

        await self.client.start(phone=self.config['phone'])

        if not await self.client.is_user_authorized():
            print("Oturum açılamadı. Lütfen tekrar deneyin.")
            return False

        print("Telegram hesabına başarıyla giriş yapıldı!")
        return True

    async def monitor_groups(self):
        """Gruplardaki mesajları izler."""
        if not self.client:
            print("İstemci başlatılmadı.")
            return

        @self.client.on(events.NewMessage())
        async def handler(event):
            """Yeni mesajları işler."""
            try:
                chat = await event.get_chat()
                chat_id = event.chat_id

                chat_identifier = f"@{chat.username}" if hasattr(chat, 'username') and chat.username else str(chat_id)

                if chat_identifier not in self.config['groups']:
                    return

                message_text = event.message.text if event.message.text else ""

                for keyword in self.config['keywords']:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', message_text, re.IGNORECASE):
                        sender = await event.get_sender()
                        sender_name = f"{sender.first_name} {sender.last_name if sender.last_name else ''}"

                        result = {
                            'keyword': keyword,
                            'group': chat_identifier,
                            'sender_name': sender_name,
                            'sender_id': sender.id,
                            'message': message_text,
                            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

                        key = f"{chat_identifier}_{keyword}"
                        self.results[key].append(result)

                        print("-" * 50)
                        print(f"Anahtar Kelime: {keyword}")
                        print(f"Grup: {chat_identifier}")
                        print(f"Gönderen: {sender_name}")
                        print(f"Mesaj: {message_text}")
                        print(f"Zaman: {result['timestamp']}")

                        self.save_results()

            except Exception as e:
                logger.error(f"Mesaj işleme hatası: {e}")

    async def start_monitoring(self):
        """İzleme işlemini başlatır."""
        if not self.config['groups']:
            print("İzlenecek grup bulunamadı. Lütfen grup ekleyin.")
            return

        if not self.config['keywords']:
            print("İzlenecek anahtar kelime bulunamadı. Lütfen anahtar kelime ekleyin.")
            return

        print("\nMonitoring başlatılıyor...")
        print(f"İzlenen gruplar: {', '.join(self.config['groups'])}")
        print(f"İzlenen anahtar kelimeler: {', '.join(self.config['keywords'])}")
        print("Çıkmak için Ctrl+C tuşlarına basın.")

        await self.monitor_groups()
        await self.client.run_until_disconnected()

    def run(self):
        """Uygulamayı çalıştırır."""
        asyncio.run(self._run_async())

    async def _run_async(self):
        """Asenkron çalıştırma."""
        try:
            if not await self.setup_client():
                return
            await self.start_monitoring()
        except KeyboardInterrupt:
            print("\nUygulama kapatılıyor...")
            self.save_results()
        finally:
            if self.client:
                await self.client.disconnect()


# Komut satırı arayüzü
def main():
    monitor = TelegramMonitor()

    while True:
        print("\n=== Telegram Monitoring Uygulaması ===")
        print("1. Uygulamayı Başlat")
        print("2. Anahtar Kelime Ekle")
        print("3. Anahtar Kelime Kaldır")
        print("4. Grup Ekle")
        print("5. Grup Kaldır")
        print("6. Yapılandırmayı Göster")
        print("0. Çıkış")

        choice = input("Seçiminiz: ")

        if choice == "1":
            monitor.run()
        elif choice == "2":
            monitor.add_keyword(input("Eklenecek anahtar kelime: "))
        elif choice == "3":
            monitor.remove_keyword(input("Kaldırılacak anahtar kelime: "))
        elif choice == "4":
            monitor.add_group(input("Eklenecek grup (örn. @grupadi veya grup linki): "))
        elif choice == "5":
            monitor.remove_group(input("Kaldırılacak grup: "))
        elif choice == "6":
            print("\nMevcut Yapılandırma:")
            print(f"API ID: {'Ayarlanmış' if monitor.config['api_id'] else 'Ayarlanmamış'}")
            print(f"API Hash: {'Ayarlanmış' if monitor.config['api_hash'] else 'Ayarlanmamış'}")
            print(f"Telefon: {monitor.config['phone']}")
            print(f"Anahtar Kelimeler: {', '.join(monitor.config['keywords'])}")
            print(f"İzlenen Gruplar: {', '.join(monitor.config['groups'])}")
        elif choice == "0":
            print("Uygulama kapatılıyor...")
            break
        else:
            print("Geçersiz seçenek.")

if __name__ == "__main__":
    main()
