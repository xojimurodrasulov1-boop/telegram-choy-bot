import asyncio
import logging
import sys
import signal

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import main_router, balance_router, support_router, vitrina_router
import admin_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Graceful shutdown uchun
shutdown_event = asyncio.Event()


async def main_bot():
    try:
        # Bot buyruqlarini sozlash - "/" yozganda ko'rsatiladi
        commands = [
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="list", description="Витрина товаров"),
            BotCommand(command="support", description="Обратная связь"),
            BotCommand(command="rules", description="Правила работы"),
            BotCommand(command="info", description="Информация о магазине")
        ]
        await bot.set_my_commands(commands)
        
        # Router tartibini o'zgartirish - balance_router birinchi bo'lishi kerak
        dp.include_router(balance_router)
        dp.include_router(support_router)
        dp.include_router(vitrina_router)
        dp.include_router(main_router)  # main_router oxirida, chunki handle_any_text bor
        
        logger.info("Main Bot ishga tushdi!")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, stop_signals=None)
    except Exception as e:
        logger.error(f"Main bot xatosi: {e}", exc_info=True)
        raise


async def admin_bot_main():
    try:
        logger.info("Admin Bot ishga tushdi!")
        await admin_bot.bot.delete_webhook(drop_pending_updates=True)
        await admin_bot.dp.start_polling(admin_bot.bot, stop_signals=None)
    except Exception as e:
        logger.error(f"Admin bot xatosi: {e}", exc_info=True)
        raise


async def main():
    # Ikkala botni parallel ishga tushirish
    try:
        await asyncio.gather(
            main_bot(),
            admin_bot_main(),
            return_exceptions=True
        )
    except Exception as e:
        logger.error(f"Bot xatosi: {e}", exc_info=True)
        raise


def signal_handler(signum, frame):
    """Signal handler - graceful shutdown"""
    logger.info(f"Signal {signum} qabul qilindi. Botlar to'xtatilmoqda...")
    shutdown_event.set()


if __name__ == "__main__":
    # Signal handlerlarni sozlash
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Botlar to'xtatildi")
    except Exception as e:
        logger.error(f"Fatal xato: {e}", exc_info=True)
        sys.exit(1)
