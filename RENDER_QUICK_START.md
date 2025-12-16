# 🚀 Render.com - Tezkor Boshlash

## 📋 Qadam 1: Service Yaratish

1. **"Create new service"** tugmasini bosing
2. **"Background Worker"** ni tanlang (⚠️ Web Service emas!)
3. GitHub repo'ni ulang:
   - Agar repo GitHub'da bo'lsa: **"Connect account"** > repo'ni tanlang
   - Agar repo yo'q bo'lsa: avval GitHub'ga push qiling

## 📋 Qadam 2: Sozlamalar

**Basic:**
- **Name**: `telegram-bot` (yoki istalgan nom)
- **Environment**: `Python 3`
- **Region**: `Singapore` yoki `Frankfurt` (eng yaqin)

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run_both.py`

## 📋 Qadam 3: Environment Variables (MUHIM!)

**Environment** bo'limiga o'ting va quyidagilarni qo'shing:

```
BOT_TOKEN = 8322186136:AAGTHTSqi0GGU9sz9HTnAnoIRAVtdcbXXp4
ADMIN_BOT_TOKEN = 8299312504:AAG13OG07n9Kz5f5y_BHyNZNgqGUvKitvvY
NOWPAYMENTS_API_KEY = jHI2pNyiWevjOHFTih8Z7PpYauJNR4ZD
```

**Qanday qo'shish:**
1. **Environment** bo'limiga o'ting
2. **"Add Environment Variable"** tugmasini bosing
3. Har birini alohida qo'shing:
   - Key: `BOT_TOKEN`, Value: `8322186136:AAGTHTSqi0GGU9sz9HTnAnoIRAVtdcbXXp4`
   - Key: `ADMIN_BOT_TOKEN`, Value: `8299312504:AAG13OG07n9Kz5f5y_BHyNZNgqGUvKitvvY`
   - Key: `NOWPAYMENTS_API_KEY`, Value: `jHI2pNyiWevjOHFTih8Z7PpYauJNR4ZD`

## 📋 Qadam 4: Deploy

1. Barcha sozlamalarni to'ldirgandan keyin
2. **"Create Background Worker"** tugmasini bosing
3. Deploy jarayoni boshlanadi (2-5 daqiqa)
4. **Logs** bo'limida kuzatib boring

## ✅ Muvaffaqiyatli Deploy

Loglarda quyidagi xabarlarni ko'rasiz:
```
Main Bot ishga tushdi!
Admin Bot ishga tushdi!
```

## ⚠️ Muhim Eslatmalar

1. **Background Worker** tanlang - Web Service emas!
2. **Environment Variables** muhim - ularni to'g'ri qo'shing!
3. **Start Command**: `python run_both.py`
4. **Build Command**: `pip install -r requirements.txt`

## 🆘 Muammo Bo'lsa

- **Logs** bo'limida xatoliklarni ko'ring
- **Environment Variables** to'g'ri qo'shilganini tekshiring
- `requirements.txt` fayli repo'da bo'lishi kerak

