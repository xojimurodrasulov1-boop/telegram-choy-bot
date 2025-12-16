# 🚀 Render.com bilan Botni 24/7 Ishga Tushirish

## ✅ Render.com - Bepul va Oson!

Render.com bepul tier mavjud va botni 24/7 ishlatish uchun juda qulay.

---

## 📋 Qadam-baqadam Qo'llanma

### 1. Render.com ga Ro'yxatdan O'tish

1. **Render.com** ga kirish: https://render.com
2. **Sign Up** tugmasini bosing
3. GitHub account bilan ro'yxatdan o'ting (tavsiya etiladi)

### 2. Yangi Service Yaratish

1. Dashboard'da **New +** tugmasini bosing
2. **Background Worker** ni tanlang (⚠️ Web Service emas!)
3. GitHub repo'ni ulang yoki kodni yuklang

### 3. Sozlamalarni To'ldirish

**Basic Settings:**
- **Name**: `telegram-bot` (yoki istalgan nom)
- **Environment**: `Python 3`
- **Region**: Eng yaqin region (masalan: `Singapore` yoki `Frankfurt`)

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run_both.py`

**Environment Variables** (muhim!):
Quyidagi o'zgaruvchilarni qo'shing:

```
BOT_TOKEN=8322186136:AAGTHTSqi0GGU9sz9HTnAnoIRAVtdcbXXp4
ADMIN_BOT_TOKEN=8299312504:AAG13OG07n9Kz5f5y_BHyNZNgqGUvKitvvY
NOWPAYMENTS_API_KEY=jHI2pNyiWevjOHFTih8Z7PpYauJNR4ZD
```

**Qanday qo'shish:**
1. **Environment** bo'limiga o'ting
2. **Add Environment Variable** tugmasini bosing
3. Har birini alohida qo'shing:
   - Key: `BOT_TOKEN`, Value: `8322186136:AAGTHTSqi0GGU9sz9HTnAnoIRAVtdcbXXp4`
   - Key: `ADMIN_BOT_TOKEN`, Value: `8299312504:AAG13OG07n9Kz5f5y_BHyNZNgqGUvKitvvY`
   - Key: `NOWPAYMENTS_API_KEY`, Value: `jHI2pNyiWevjOHFTih8Z7PpYauJNR4ZD`

### 4. Deploy Qilish

1. Barcha sozlamalarni to'ldirgandan keyin
2. **Create Background Worker** tugmasini bosing
3. Deploy jarayoni boshlanadi (2-5 daqiqa)
4. Loglarni kuzatib boring

---

## 🔍 Deploy Jarayonini Tekshirish

### Loglarni Ko'rish:
1. Service'ga kirish
2. **Logs** bo'limiga o'tish
3. Quyidagi xabarlarni ko'rasiz:
   ```
   Main Bot ishga tushdi!
   Admin Bot ishga tushdi!
   ```

### Agar Xatolik Bo'lsa:
- Loglarni tekshiring
- Environment variables to'g'ri qo'shilganini tekshiring
- `requirements.txt` fayli mavjudligini tekshiring

---

## 💾 Database Fayllarini Saqlash

⚠️ **MUHIM:** Render.com'da fayllar har safar restart qilinganda yo'qoladi!

**Yechim:**
1. **Persistent Disk** qo'shing (bepul tier'da mavjud)
2. Yoki database'ni cloud'ga ko'chiring (PostgreSQL, MongoDB)

**Hozircha:**
- Database fayllari (`data/users.json`, `data/orders.json`) har safar yangilanadi
- Production'da PostgreSQL yoki MongoDB ishlatish tavsiya etiladi

---

## 🔄 Restart Qilish

### Qo'lda Restart:
1. Service'ga kirish
2. **Manual Deploy** > **Deploy latest commit**

### Avtomatik Restart:
- Kod o'zgarganda (GitHub push) avtomatik restart qiladi
- Xatolik bo'lsa, Render avtomatik restart qiladi

---

## 📊 Monitoring

### Status Tekshirish:
- Dashboard'da service status ko'rsatiladi
- **Logs** bo'limida real-time loglar

### Xatoliklarni Kuzatish:
- **Logs** bo'limida barcha xatoliklar ko'rsatiladi
- Email orqali xatoliklar haqida xabar olish mumkin

---

## 💰 Narx

✅ **Bepul Tier:**
- 750 soat/oy (24/7 ishlaydi!)
- 512 MB RAM
- Background Worker uchun bepul

⚠️ **Cheklovlar:**
- Agar 15 daqiqa ishlatilmasa, uxlab qoladi
- Lekin Background Worker doim ishlaydi!

---

## 🎯 Render vs Railway

| Xususiyat | Render | Railway |
|-----------|--------|---------|
| Bepul soat | 750 soat/oy | 500 soat/oy |
| Background Worker | ✅ Bepul | ✅ Bepul |
| Avtomatik Deploy | ✅ | ✅ |
| Loglar | ✅ | ✅ |
| Osonlik | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 📝 Muhim Eslatmalar

1. **Environment Variables** muhim - ularni to'g'ri qo'shing!
2. **Background Worker** tanlang - Web Service emas!
3. **Start Command**: `python run_both.py`
4. **Build Command**: `pip install -r requirements.txt`
5. Database fayllari saqlanib qolishi uchun Persistent Disk qo'shing

---

## 🆘 Muammo Bo'lsa

1. **Loglarni tekshiring** - barcha xatoliklar u yerda
2. **Environment Variables** to'g'ri qo'shilganini tekshiring
3. **Requirements.txt** fayli mavjudligini tekshiring
4. Render support'ga murojaat qiling

---

## ✅ Tayyor!

Bot endi 24/7 ishlaydi va bepul! 🎉

