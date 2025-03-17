# TGDashboard

TGDashboard, belirlenen Telegram gruplarındaki mesajları izleyerek, belirli anahtar kelimeleri içeren mesajları tespit eden bir Python uygulamasıdır.

## Özellikler
- Telegram gruplarından mesaj izleme
- Belirli anahtar kelimeleri içeren mesajları kaydetme
- İzlenecek grupları ve anahtar kelimeleri özelleştirme
- Sonuçları JSON formatında kaydetme

## Gereksinimler
Projeyi çalıştırmadan önce aşağıdaki bağımlılıkların yüklü olduğundan emin olun:

- Python 3.7 veya daha yeni bir sürüm
- `telethon`
- `asyncio`

Bağımlılıkları yüklemek için aşağıdaki komutu çalıştırabilirsiniz:
```sh
pip install telethon
```

## Kurulum ve Kullanım

1. **Depoyu Kopyalayın**
   ```sh
   git clone https://github.com/kullaniciadi/tgdashboard.git
   cd tgdashboard
   ```

2. **Yapılandırma Dosyasını Ayarlayın**
   İlk çalıştırmada, `config.json` dosyası oluşturulacaktır. Bu dosyayı aşağıdaki şekilde düzenleyin:
   ```json
   {
       "api_id": "TELEGRAM_API_ID",
       "api_hash": "TELEGRAM_API_HASH",
       "phone": "+901234567890",
       "keywords": ["örnek", "anahtar", "kelime"],
       "groups": ["@grupadi"],
       "save_results": true,
       "results_file": "results.json"
   }
   ```

3. **Uygulamayı Çalıştırın**
   ```sh
   python tgdashboard.py
   ```
   Başlangıçta telefon numaranızı girerek Telegram hesabınıza giriş yapmanız gerekecektir.

4. **Anahtar Kelime veya Grup Ekleme/Kaldırma**
   Uygulama çalıştırıldıktan sonra aşağıdaki seçeneklerden biriyle yönetim yapabilirsiniz:
   - **Anahtar Kelime Ekle:** `2`
   - **Anahtar Kelime Kaldır:** `3`
   - **Grup Ekle:** `4`
   - **Grup Kaldır:** `5`
   - **Mevcut Yapılandırmayı Görüntüle:** `6`
   - **Çıkış:** `0`

## Sonuçlar
Elde edilen sonuçlar `results.json` dosyasında saklanacaktır. Örnek bir çıktı:
```json
{
    "@grupadi_ornek": [
        {
            "keyword": "ornek",
            "group": "@grupadi",
            "sender_name": "Ali Veli",
            "sender_id": 123456789,
            "message": "Bu bir örnek mesajdır.",
            "timestamp": "2025-03-17 12:34:56"
        }
    ]
}
```

## Sorun Giderme
- **Oturum açma başarısız:** `config.json` içindeki `api_id`, `api_hash` ve `phone` bilgilerini kontrol edin.
- **Bağlantı hatası:** Telegram API erişiminizin engellenmediğinden emin olun.
- **Sonuçlar kaydedilmiyor:** `save_results` değişkeninin `true` olduğundan emin olun ve `results_file` dosyasının yazılabilir olduğunu kontrol edin.

## İletişim
Herhangi bir sorun yaşarsanız veya katkıda bulunmak isterseniz, [@ugurayydogan](https://instagram.com/ugurayydogan) ile iletişime geçebilirsiniz.
