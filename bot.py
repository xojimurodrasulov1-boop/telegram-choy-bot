import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import main_router, balance_router, support_router, vitrina_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    # Bot buyruqlarini sozlash - "/" yozganda ko'rsatiladi
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="list", description="Витрина товаров"),
        BotCommand(command="support", description="Обратная связь"),
        BotCommand(command="rules", description="Правила работы"),
        BotCommand(command="info", description="Информация о магазине")
    ]
    await bot.set_my_commands(commands)
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Router tartibini o'zgartirish - balance_router birinchi bo'lishi kerak
    dp.include_router(balance_router)
    dp.include_router(support_router)
    dp.include_router(vitrina_router)
    dp.include_router(main_router)  # main_router oxirida, chunki handle_any_text bor
    
    logger.info("Bot ishga tushdi!")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
