from telethon import TelegramClient, events
import asyncio
import re
import os
import datetime
import json
from collections import defaultdict
import logging

# Logging ayarları (uygulama problemliyse contact @ugurayydogan instagram hesabımdan ulaşabilirsiniz.)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Yapılandırma dosyası API girmen gerekiyor ben daha sonra girecegim.
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
            # Varsayılan yapılandırma
            default_config = {
                'api_id': '',  # Telegram API ID
                'api_hash': '',  # Telegram API Hash
                'phone': '',  # Telefon numarası
                'keywords': ['Turkey'],  # İzlenecek anahtar kelimeler
                'groups': [],  # İzlenecek gruplar
                'save_results': True,  # Sonuçları kaydetme
                'results_file': 'results.json'  # Sonuç dosyası
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            print(f"Lütfen {CONFIG_FILE} dosyasını düzenleyiniz.")
            return default_config
    
    def save_config(self):
        """Yapılandırmayı dosyaya kaydeder."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
    
    def add_keyword(self, keyword):
        """Yeni bir anahtar kelime ekler."""
        if keyword not in self.config['keywords']:
            self.config['keywords'].append(keyword)
            self.save_config()
            print(f"Anahtar kelime eklendi: {keyword}")
        else:
            print(f"Anahtar kelime zaten mevcut: {keyword}")
    
    def remove_keyword(self, keyword):
        """Bir anahtar kelimeyi kaldırır."""
        if keyword in self.config['keywords']:
            self.config['keywords'].remove(keyword)
            self.save_config()
            print(f"Anahtar kelime kaldırıldı: {keyword}")
        else:
            print(f"Anahtar kelime bulunamadı: {keyword}")
    
    def add_group(self, group_link):
        """İzlenecek bir grup ekler."""
        if group_link not in self.config['groups']:
            self.config['groups'].append(group_link)
            self.save_config()
            print(f"Grup eklendi: {group_link}")
        else:
            print(f"Grup zaten izleniyor: {group_link}")
    
    def remove_group(self, group_link):
        """İzlenen bir grubu kaldırır."""
        if group_link in self.config['groups']:
            self.config['groups'].remove(group_link)
            self.save_config()
            print(f"Grup kaldırıldı: {group_link}")
        else:
            print(f"Grup bulunamadı: {group_link}")
    
    def save_results(self):
        """Sonuçları dosyaya kaydeder."""
        if self.config['save_results']:
            with open(self.config['results_file'], 'w', encoding='utf-8') as f:
                json.dump(dict(self.results), f, indent=4)
            print(f"Sonuçlar {self.config['results_file']} dosyasına kaydedildi.")
    
    async def setup_client(self):
        """Telegram istemcisini ayarlar ve oturum açar."""
        if not self.config['api_id'] or not self.config['api_hash']:
            print("Lütfen config.json dosyasında api_id ve api_hash değerlerini ayarlayın.")
            return False
        
        # Oturum dosyası için kullanıcı telefon numarasını kullan
        session_file = f"session_{self.config['phone']}"
        
        self.client = TelegramClient(session_file, 
                                    self.config['api_id'], 
                                    self.config['api_hash'])
        
        await self.client.start(phone=self.config['phone'])
        
        if not await self.client.is_user_authorized():
            print("Oturum açılamadı. Lütfen tekrar deneyin.")
            return False
        
        print("Telegram hesabına başarıyla giriş yapıldı!")
        return True
    
    async def monitor_groups(self):
        """Belirlenen gruplardaki mesajları izler."""
        if not self.client:
            print("İstemci başlatılmadı.")
            return
        
        @self.client.on(events.NewMessage())
        async def handler(event):
            """Yeni mesajları işler."""
            # Mesaj bir gruptan geliyorsa ve izlenen gruplardan biriyse
            try:
                chat = await event.get_chat()
                chat_id = event.chat_id
                
                # Grubun username'ini veya ID'sini al örneğin @uguraydogan
                if hasattr(chat, 'username') and chat.username:
                    chat_identifier = f"@{chat.username}"
                else:
                    chat_identifier = str(chat_id)
                
                # Grup listesinde yoksa işleme
                if chat_identifier not in self.config['groups']:
                    return
                
                # Mesaj içeriğini al
                message_text = event.message.text if event.message.text else ""
                
                # Anahtar kelimeleri kontrol et
                for keyword in self.config['keywords']:
                    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    if pattern.search(message_text):
                        # Mesaj bilgilerini ekle
                        sender = await event.get_sender()
                        sender_name = f"{sender.first_name} {sender.last_name if sender.last_name else ''}"
                        sender_id = sender.id
                        
                        result = {
                            'keyword': keyword,
                            'group': chat_identifier,
                            'sender_name': sender_name,
                            'sender_id': sender_id,
                            'message': message_text,
                            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Sonuçları kaydet
                        key = f"{chat_identifier}_{keyword}"
                        self.results[key].append(result)
                        
                        # Terminal çıktısı
                        print("-" * 50)
                        print(f"Anahtar Kelime: {keyword}")
                        print(f"Grup: {chat_identifier}")
                        print(f"Gönderen: {sender_name}")
                        print(f"Mesaj: {message_text}")
                        print(f"Zaman: {result['timestamp']}")
                        
                        # Belirli aralıklarla sonuçları kaydet
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
        
        # İstemciyi burada çalıştır
        await self.client.run_until_disconnected()
    
    def run(self):
        """Uygulamayı çalıştırır."""
        loop = asyncio.get_event_loop()
        
        try:
            # İstemciyi ayarlayalım
            setup_success = loop.run_until_complete(self.setup_client())
            if not setup_success:
                return
            
            # İzlemeyi başlatalım
            loop.run_until_complete(self.start_monitoring())
        except KeyboardInterrupt:
            print("\nUygulama kapatılıyor...")
            self.save_results()
        finally:
            if self.client:
                loop.run_until_complete(self.client.disconnect())
            loop.close()


# Basit bir komut satırı arayüzü burası kişiye göre geliştirilebilir
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
            keyword = input("Eklenecek anahtar kelime: ")
            monitor.add_keyword(keyword)
        elif choice == "3":
            keyword = input("Kaldırılacak anahtar kelime: ")
            monitor.remove_keyword(keyword)
        elif choice == "4":
            group = input("Eklenecek grup (örn. @grupadi veya grup linki): ")
            monitor.add_group(group)
        elif choice == "5":
            group = input("Kaldırılacak grup: ")
            monitor.remove_group(group)
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