import asyncio
import json
from aiogram import Bot
from config import BOT_TOKEN

async def broadcast():
    bot = Bot(token=BOT_TOKEN)
    
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    message = """⚠️ <b>Texnik nosozlik</b>

Bot 2 soat mobaynida yopiq bo'ladi.

Noqulaylik uchun uzr so'raymiz! 🙏"""
    
    for user_id in users:
        try:
            await bot.send_message(int(user_id), message, parse_mode="HTML")
            print(f"✅ Yuborildi: {user_id}")
        except Exception as e:
            print(f"❌ Yuborilmadi {user_id}: {e}")
    
    await bot.session.close()
    print("\n✅ Barcha foydalanuvchilarga xabar yuborildi!")

asyncio.run(broadcast())
