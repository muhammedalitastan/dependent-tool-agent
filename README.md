# 🤖 Tool-Calling Agent - Project 2

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Birbirine bağımlı araç kullanımı (tool-calling) ile kullanıcı taleplerini işleyen akıllı asistan sistemi.

## 📋 Proje Hedefi

Bu proje, kullanıcının talebini anlayıp, gerekli dış fonksiyonları (tool/API) doğru sırayla çağırarak sonuca ulaşan ve eksik bilgi durumunda inisiyatif alabilen bir LLM Agent'ı içerir.

## ✨ Temel Özellikler

### 🔗 Bağımlı Araç Kullanımı (Chaining)
- **3 Temel Araç**: `get_user_details()`, `get_recent_transactions()`, `check_fraud_reason()`
- **Araç Zinciri**: Bir aracın çıktısı diğerinin girdisi olarak kullanılır
- **Sıralı Çalışma**: Araçlar doğru sırada çağrılır

### 🧠 Akıllı Intent Analizi
- **Entity Extraction**: E-posta, işlem ID, limit gibi bilgileri otomatik çıkarma
- **Intent Detection**: Kullanıcı niyetini belirleme (ödeme sorunu, işlem geçmişi, kullanıcı bilgisi, aktivite analizi)
- **Error Handling**: Tüm hata senaryolarını yakalama

### 🛡️ Hata Yönetimi
- **Eksik Paramatre**: E-posta adresi eksikse kullanıcıdan iste
- **Geçersiz Veri**: Var olmayan kullanıcı veya işlem için anlaşılır mesajlar
- **Sistem Hataları**: Beklenmedik durumları yönetme

## 🏗️ Mimari

### Sistem Bileşenleri

```
📦 Tool-Calling Agent
├── 📁 src/
│   ├── 🤖 agent.py                  # Ana agent sistemi
│   ├── 🔧 tools.py                  # API araçları yönetimi
│   └── �️ database.py              # Mock veritabanı
├── 📁 data/
│   └── 🗄️ mock_database.json        # Sahte veritabanı
├── 📁 tests/
│   └── 🧪 test_advanced_agent.py    # Test senaryoları
├── 🚀 main.py                      # Ana uygulama
├── 📖 README.md                    # Dokümantasyon
└── ⚙️ requirements.txt             # Bağımlılıklar
```

## 🔧 3 Temel Araç

### 1. get_user_details(email: str)
E-posta adresini alıp kullanıcı ID'si ve hesap durumunu döndürür.
- **Girdi**: E-posta adresi
- **Çıktı**: Kullanıcı ID, ad, durum, kayıt tarihi
- **Hata**: Sistemde olmayan e-posta için hata fırlatır

### 2. get_recent_transactions(user_id: str, limit: int)
Kullanıcının son işlemlerini döndürür.
- **Girdi**: Kullanıcı ID'si, limit (1-50 arası)
- **Çıktı**: İşlem listesi (işlem numarası, miktar, durum)
- **Hata**: Geçersiz kullanıcı ID veya limit için hata fırlatır

### 3. check_fraud_reason(transaction_id: str)
Başarısız bir işlemin neden reddedildiğini döndürür.
- **Girdi**: İşlem ID'si
- **Çıktı**: Fraud nedeni, detaylı kod, tespit zamanı
- **Hata**: İşlem bulunamazsa veya fraud kaydı yoksa hata fırlatır

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip

### Adım 1: Depoyu klonlayın
```bash
git clone <repository-url>
cd project2-tool-calling-agent
```

### Adım 2: Sanal ortam oluşturun (önerilir)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### Adım 3: Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

## 🎯 Kullanım

### Interaktif Mod
```bash
python main.py
```

### Test Modu
```bash
python main.py --test
```

### Örnek Komutlar

1. **Ödeme Sorunu Sorgulama:**
   ```
   ali@sirket.com adresli hesabımla dün yapmaya çalıştığım ödeme neden reddedildi?
   ```

2. **İşlem Geçmişi:**
   ```
   ayse@sirket.com adresli hesabımın son 5 işlemini göster
   ```

3. **Kullanıcı Bilgisi:**
   ```
   mehmet@sirket.com hakkında bilgi ver
   ```

4. **Aktivite Analizi:**
   ```
   zeynep@sirket.com adresli hesabın aktivitesini analiz et
   ```

## 🔄 Tool Chaining Örneği

### Senaryo: Ödeme Sorunu
**Kullanıcı Sorgusu:** `"ali@sirket.com adresli hesabımla dün yapmaya çalıştığım ödeme neden reddedildi?"`

### Agent İşlem Akışı:
1. **Intent Detection**: `check_payment_failure`
2. **Entity Extraction**: `email = "ali@sirket.com"`
3. **Tool Chain**:
   - `get_user_details("ali@sirket.com")` → `user_id = "USR001"`
   - `get_failed_transactions_for_user("ali@sirket.com")` → `failed_transactions`
   - `check_fraud_reason("TRX001")` → `fraud_reason`
4. **Response**: Kullanıcıya anlamlı cevap formatla

### Eksik Parametre Yönetimi
**Kullanıcı Sorgusu:** `"dün yaptığım ödeme neden reddedildi?"`

**Agent Cevabı:** `"Ödeme sorunu sorgulamak için lütfen e-posta adresinizi belirtin. Örnek: 'ali@sirket.com adresli hesabımla dün yapmaya çalıştığım ödeme neden reddedildi?'"`

## 🗄️ Veritabanı Yapısı

### Mock Database
Proje gerçek veritabanı yerine JSON dosyası kullanır:
- **Kullanıcılar**: `users` array (user_id, email, name, status)
- **İşlemler**: `transactions` array (transaction_id, user_id, amount, status)
- **Fraud Nedenleri**: `fraud_reasons` array (transaction_id, reason, detailed_code)

### Test Edilebilirlik
Veri dosyası kolayca değiştirilebilir:
1. **Yeni Kullanıcı Ekleme**: `users` array'ine yeni kayıt
2. **Yeni İşlem Ekleme**: `transactions` array'ine yeni kayıt  
3. **Fraud Nedeni Değiştirme**: `fraud_reasons`'ta güncelleme

## 🧪 Test Senaryoları

### Manuel Test
```bash
python test_missing_params.py
```

### Otomatik Test
```bash
python main.py --test
```

### Test Edilen Durumlar
- ✅ Eksik e-posta parametresi
- ✅ Geçersiz e-posta formatı
- ✅ Var olmayan kullanıcı
- ✅ Tool chaining (bağımlı araçlar)
- ✅ Hata yönetimi
- ✅ Anlaşılamayan sorgular

## Lisans

MIT License
