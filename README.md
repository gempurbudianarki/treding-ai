# 🤖 AI Trading Bot — XAUUSD Automated Intelligence

Bot trading otomatis untuk XAUUSD yang menggabungkan analisa teknikal, sentimen, dan eksekusi trading real-time.  
Dilengkapi dashboard UI dark mewah seperti TradingView/Binance yang bisa mengontrol bot secara langsung.

---

## 🚀 1. Overview Sistem

Proyek ini adalah **AI Trading Bot modular** yang berjalan dalam loop berulang, mengambil data market, menganalisa, menghasilkan sinyal, lalu mengeksekusi BUY/SELL otomatis di MT5.

Bot ini memiliki:

- 📡 Market data feed (candlestick MT5)
- 📊 Technical analysis engine
- 📰 Sentiment analysis engine (berita)
- 🧠 Decision AI (BUY / SELL / HOLD)
- 🖥 Dashboard kontrol bot
- 🧾 Trade logger + history

Semua berjalan otomatis berdasarkan timeframe yang dipilih.

---

## ⚙️ 2. Alur Sistem (System Flow)

### **STEP 1 — Feeder (Data Market)**
Bot mengambil:
- Candlestick O/H/L/C
- Volume
- Timeframe (default M5)
- Harga XAUUSD terbaru
- Berita terkait gold/market

Output disimpan sebagai `status.json`.

---

### **STEP 2 — Technical Brain**
Analisa indikator:
- EMA Fast/Slow  
- RSI  
- MACD  
- Stochastic  
- ATR  
- Trend & Momentum  

Output:
```json
{
  "direction": "buy/sell/neutral",
  "confidence": 0.0-1.0
}
```

---

### **STEP 3 — Sentiment Brain (AI)**
Analisa news / headlines:
- tone market  
- bullish / bearish pressure  
- risk event  

Output:
```json
{
  "sentiment": "bullish/bearish/neutral",
  "confidence": 0.0-1.0
}
```

---

### **STEP 4 — Condition Brain**
Cek kondisi pasar:
- volatilitas tinggi  
- sesi market buruk  
- news merah  
- sideways detection  

Output:
```
"safe" / "warn" / "avoid"
```

---

### **STEP 5 — Orchestrator (Decision Engine)**

Menggabungkan semua brain:

```
technical + sentiment + condition + mode → BUY/SELL/HOLD
```

Jika confidence cocok dan MODE mengizinkan → bot eksekusi order ke MT5.

---

### **STEP 6 — Eksekusi Trading**
Jika `trading_enabled = true`, bot kirim:
- BUY atau SELL
- Lot sesuai MODE
- Auto SL / TP
- Catat ke `trades.json`

Kalau `DRY_RUN = ON`, bot hanya simulasi.

---

### **STEP 7 — Update Dashboard**
Dashboard membaca:
- status.json  
- control.json  
- signals.json  
- trades.json  

Semua update real-time setiap loop.

---

## 🧩 3. Mode Trading (Risk Profile)

| Mode | Karakter | Risiko |
|------|----------|--------|
| SAFE | entry sedikit, filtrasi ketat | rendah |
| BALANCED | default, normal | medium |
| AGGRESSIVE | entry lebih cepat & banyak | tinggi |
| SCALPING_M5 | fast-entry, TP kecil | tinggi |

Mode diatur lewat dashboard dan langsung berdampak ke decision engine.

---

## 🖥 4. Dashboard Features

Dibangun menggunakan Flask + HTML + CSS + JS.

Fitur:  
✔ ON/OFF trading bot  
✔ Ganti MODE bot (SAFE → AGGRESSIVE)  
✔ Live price chart  
✔ Sinyal AI realtime  
✔ Riwayat trade  
✔ Open positions  
✔ Log aktivitas bot  
✔ Status loop terakhir  
✔ Technical Bias  
✔ Sentiment Market  
✔ Dark UI premium

Dashboard membaca data via `control.json`.

---

## 🔁 5. Loop Kerja Bot (Simplified Pseudocode)

```python
while True:
    data = fetch_market()
    
    tech = technical_brain(data)
    sent = sentiment_brain(data)
    cond = condition_brain(data)

    decision = orchestrator(tech, sent, cond, mode)

    if trading_enabled:
        execute_trade(decision)

    update_status_json()
    sleep(timeframe)
```

---

## 🛠 6. Cara Menjalankan

### 1️⃣ Aktifkan virtual environment
```bash
.\venv\Scripts\activate
```

### 2️⃣ Jalankan bot
```bash
python -m core.main_loop
```

### 3️⃣ Jalankan Dashboard
```bash
python dashboard_web.py
```

### 4️⃣ Akses Dashboard
```
http://127.0.0.1:5000
```

---

## 📁 7. File Penting

| File | Fungsi |
|------|--------|
| status.json | laporan analisa terbaru |
| control.json | ON/OFF bot, mode, dll |
| trades.json | histori transaksi |
| signals.json | sinyal AI |
| dashboard_web.py | web dashboard |
| main_loop.py | loop utama bot |

---

## 🎯 8. Tujuan Proyek
- Studi kasus trading algorithmic  
- membangun sistem auto-trading modular  
- riset kombinasi teknikal + sentimen  
- portfolio backend + AI + trading  
- automation dengan risiko terkontrol  

---

## 🏆 9. Credits
Dikembangkan oleh **Gempur Budi Anarki** & AI Partner (ChatGPT).  
Full support trading bot, AI module, dan UI dashboard.

---

