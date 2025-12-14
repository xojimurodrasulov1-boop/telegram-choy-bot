import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import (
    main_router,
    balance_router,
    product_router,
    support_router
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(main_router)
    dp.include_router(balance_router)
    dp.include_router(product_router)
    dp.include_router(support_router)
    
    logger.info("Bot ishga tushdi!")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
