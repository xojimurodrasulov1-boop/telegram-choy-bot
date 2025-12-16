import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

from config import ADMIN_BOT_TOKEN

bot = Bot(token=ADMIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    print(f"Received /start from {message.from_user.id}")
    await message.answer(f"Salom! Sizning ID: {message.from_user.id}")


@dp.message()
async def any_message(message: Message):
    print(f"Received message: {message.text}")
    await message.answer(f"Siz yozdingiz: {message.text}")


async def main():
    print("Test admin bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
