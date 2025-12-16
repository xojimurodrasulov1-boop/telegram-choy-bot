# Botni 24/7 Ishga Tushirish Qo'llanmasi

## 🚀 Variant 1: Railway.app (Tavsiya etiladi - Bepul)

### Qadamlar:
1. **Railway.app** ga kirish: https://railway.app
2. GitHub account bilan ro'yxatdan o'tish
3. **New Project** > **Deploy from GitHub repo**
4. Repo'ni tanlash va deploy qilish
5. **Variables** bo'limiga quyidagilarni qo'shish:
   - `BOT_TOKEN` = `8322186136:AAGTHTSqi0GGU9sz9HTnAnoIRAVtdcbXXp4`
   - `ADMIN_BOT_TOKEN` = `8299312504:AAG13OG07n9Kz5f5y_BHyNZNgqGUvKitvvY`
   - `NOWPAYMENTS_API_KEY` = `jHI2pNyiWevjOHFTih8Z7PpYauJNR4ZD`
6. **Settings** > **Service Type** > **Worker** tanlash
7. Deploy qilish

✅ **Afzalliklari:**
- Bepul tier mavjud (500 soat/oy)
- Avtomatik restart
- GitHub bilan integratsiya
- Loglarni ko'rish oson

---

## 🌐 Variant 2: Render.com (Bepul)

### Qadamlar:
1. **Render.com** ga kirish: https://render.com
2. GitHub account bilan ro'yxatdan o'tish
3. **New** > **Background Worker**
4. Repo'ni tanlash
5. **Environment Variables** qo'shish:
   - `BOT_TOKEN`
   - `ADMIN_BOT_TOKEN`
   - `NOWPAYMENTS_API_KEY`
6. **Build Command**: `pip install -r requirements.txt`
7. **Start Command**: `python run_both.py`
8. Deploy qilish

✅ **Afzalliklari:**
- Bepul tier mavjud
- Avtomatik restart
- Loglarni ko'rish

---

## 💻 Variant 3: O'z Serverida (Systemd)

### Qadamlar:

1. **Service faylini yaratish:**
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

2. **Quyidagi kontentni yozish:**
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram_group_creator
Environment="PATH=/path/to/telegram_group_creator/venv/bin"
ExecStart=/path/to/telegram_group_creator/venv/bin/python /path/to/telegram_group_creator/run_both.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

3. **Service'ni ishga tushirish:**
```bash
# Service'ni yuklash
sudo systemctl daemon-reload

# Service'ni ishga tushirish
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Status tekshirish
sudo systemctl status telegram-bot

# Loglarni ko'rish
sudo journalctl -u telegram-bot -f
```

✅ **Afzalliklari:**
- To'liq nazorat
- Bepul
- Tez ishlaydi

---

## 🖥️ Variant 4: Screen/Tmux (Oddiy)

### Screen bilan:

```bash
# Screen o'rnatish (agar yo'q bo'lsa)
# macOS: brew install screen
# Linux: sudo apt-get install screen

# Screen session yaratish
screen -S telegram-bot

# Botni ishga tushirish
cd /Users/xoji/Documents/telegram_group_creator
source venv/bin/activate
python run_both.py

# Screen'dan chiqish (Ctrl+A, keyin D)
# Qayta kirish: screen -r telegram-bot
```

### Tmux bilan:

```bash
# Tmux o'rnatish (agar yo'q bo'lsa)
# macOS: brew install tmux
# Linux: sudo apt-get install tmux

# Tmux session yaratish
tmux new -s telegram-bot

# Botni ishga tushirish
cd /Users/xoji/Documents/telegram_group_creator
source venv/bin/activate
python run_both.py

# Tmux'dan chiqish (Ctrl+B, keyin D)
# Qayta kirish: tmux attach -t telegram-bot
```

✅ **Afzalliklari:**
- O'rnatish oson
- Terminal orqali boshqarish
- Bepul

---

## 📝 Muhim Eslatmalar:

1. **Environment Variables:**
   - `.env` faylida yoki platformaning environment variables'ida bo'lishi kerak
   - Tokenlar xavfsiz saqlanishi kerak

2. **Database fayllari:**
   - `data/users.json`
   - `data/orders.json`
   - `data/reviews.json`
   - Bu fayllar saqlanib qolishi kerak (persistent storage)

3. **Rasmlar:**
   - `images/` papkasi
   - `eurohash.jpg`
   - Bu fayllar ham saqlanib qolishi kerak

4. **Loglarni tekshirish:**
   - Railway: Dashboard > Logs
   - Render: Logs bo'limi
   - Systemd: `sudo journalctl -u telegram-bot -f`
   - Screen/Tmux: session ichida

5. **Restart qilish:**
   - Railway/Render: Avtomatik yoki qo'lda redeploy
   - Systemd: `sudo systemctl restart telegram-bot`
   - Screen/Tmux: Botni to'xtatib, qayta ishga tushirish

---

## 🎯 Eng Oson Variant:

**Railway.app** - eng oson va bepul. Faqat GitHub repo'ni ulash va deploy qilish kifoya!

