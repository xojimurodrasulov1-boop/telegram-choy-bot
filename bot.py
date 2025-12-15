import asyncio
import logging
import sys
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, ADMIN_IDS, LTC_ADDRESS, BTC_ADDRESS
from data.models import db
from handlers import (
    main_router,
    balance_router,
    support_router
)

# MAHSULOTLAR
PRODUCTS = {
    "coco_120": {
        "name": "🍫Euro Hash | 0.5g",
        "price_usd": 19,
        "old_price_usd": 21,
        "description": "💯Лучший в своем деле💯\n\nEuro Hash сможет это сделать с одной плюшки😏"
    },
    "coco_200": {
        "name": "🍫Euro Hash | 1g",
        "price_usd": 42,
        "old_price_usd": None,
        "description": "💯Лучший в своем деле💯\n\nEuro Hash сможет это сделать с одной плюшки😏"
    }
}

DISTRICTS = {
    "chilonzor": "Чилонзор",
    "sergeli": "Сергели",
    "mirzoulugbek": "Мирзо Улугбек"
}

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
    dp.include_router(support_router)
    
    logger.info("Bot ishga tushdi!")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
