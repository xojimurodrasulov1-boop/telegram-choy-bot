# Bot Deployment Qo'llanmasi

## 24/7 Ishga tushirish

### Variant 1: Railway (Tavsiya etiladi)
1. Railway.app ga kirish
2. New Project > Deploy from GitHub repo
3. Environment Variables qo'shish:
   - `BOT_TOKEN`
   - `ADMIN_BOT_TOKEN`
   - `NOWPAYMENTS_API_KEY`
4. Deploy qilish

### Variant 2: Render
1. Render.com ga kirish
2. New > Web Service
3. GitHub repo'ni ulash
4. Environment Variables qo'shish
5. Deploy qilish

### Variant 3: Systemd Service (O'z serverida)
```bash
# Service faylini ko'chirish
sudo cp telegram-bot.service /etc/systemd/system/

# Service'ni ishga tushirish
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Status tekshirish
sudo systemctl status telegram-bot

# Loglarni ko'rish
sudo journalctl -u telegram-bot -f
```

## Kod o'zgartirganda

### Railway/Render:
- Avtomatik restart qiladi (git push qilganda)

### Systemd:
- Service avtomatik restart qiladi (xato bo'lsa)
- Qo'lda restart: `sudo systemctl restart telegram-bot`

## Muhim eslatmalar:
- Bot tokenlar `.env` faylida yoki environment variables'da bo'lishi kerak
- Database fayllari (`data/users.json`, `data/orders.json`) saqlanib qolishi kerak
- Loglarni muntazam tekshirish kerak

