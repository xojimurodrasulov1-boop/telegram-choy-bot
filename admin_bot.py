import asyncio
import logging
import sys
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import ADMIN_BOT_TOKEN, BOT_TOKEN, ADMIN_IDS
from data.models import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

bot = Bot(token=ADMIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

pending_applications = {}


def get_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Заявки", callback_data="show_applications")
            ],
            [
                InlineKeyboardButton(text="👥 Пользователи", callback_data="show_users")
            ]
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    print(f"User ID: {message.from_user.id}")
    if message.from_user.id not in ADMIN_IDS:
        await message.answer(f"⛔ Доступ запрещен!\n\nВаш ID: <code>{message.from_user.id}</code>", parse_mode="HTML")
        return
    
    await message.answer(
        "🔐 <b>ADMIN PANEL</b>\n\n"
        "Добро пожаловать в панель администратора!\n"
        "Выберите действие:",
        reply_markup=get_admin_menu(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "show_applications")
async def show_applications(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    if not pending_applications:
        await callback.answer("📭 Нет новых заявок", show_alert=True)
        return
    
    text = "📋 <b>АКТИВНЫЕ ЗАЯВКИ</b>\n\n"
    for app_id, app_data in pending_applications.items():
        text += f"🆔 #{app_id}\n"
        text += f"👤 {app_data.get('username', 'Unknown')}\n"
        text += f"💰 {app_data.get('amount', 0)} $\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n"
    
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]]
    )
    
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")


@dp.callback_query(F.data == "show_users")
async def show_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    users = db.get_all_users()
    
    if not users:
        await callback.answer("👥 Нет пользователей", show_alert=True)
        return
    
    text = "👥 <b>ПОЛЬЗОВАТЕЛИ</b>\n\n"
    for user in users[:20]:
        text += f"🆔 <code>{user.user_id}</code>\n"
        text += f"👤 {user.full_name}\n"
        text += f"💰 Баланс: {user.balance} $\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n"
    
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]]
    )
    
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔐 <b>ADMIN PANEL</b>\n\n"
        "Добро пожаловать в панель администратора!\n"
        "Выберите действие:",
        reply_markup=get_admin_menu(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("confirm_deposit:"))
async def confirm_deposit(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    
    user_id = int(parts[1])
    amount = int(parts[2])
    application_id = parts[3]
    
    db.update_balance(user_id, amount)
    user = db.get_user(user_id)
    
    pending_applications.pop(application_id, None)
    
    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ <b>ПОДТВЕРЖДЕНО</b>\n"
        f"Баланс пользователя пополнен на {amount} $",
        parse_mode="HTML"
    )
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": user_id,
            "text": (
                f"✅ <b>Ваш платеж подтвержден!</b>\n\n"
                f"🆔 Заявка: #{application_id}\n"
                f"➕ Начислено: {amount} $\n"
                f"💰 Ваш баланс: {user.balance} $\n\n"
                f"Спасибо за пополнение! 🙏"
            ),
            "parse_mode": "HTML"
        }
        await session.post(url, json=payload)
    
    await callback.answer("✅ Платеж подтвержден!")


@dp.callback_query(F.data.startswith("reject_deposit:"))
async def reject_deposit(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    
    user_id = int(parts[1])
    application_id = parts[2]
    
    pending_applications.pop(application_id, None)
    
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>ОТКЛОНЕНО</b>",
        parse_mode="HTML"
    )
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": user_id,
            "text": (
                f"❌ <b>Ваш платеж отклонен</b>\n\n"
                f"🆔 Заявка: #{application_id}\n\n"
                f"Причина: Платеж не найден или неверная сумма.\n"
                f"Обратитесь в поддержку."
            ),
            "parse_mode": "HTML"
        }
        await session.post(url, json=payload)
    
    await callback.answer("❌ Платеж отклонен!")


async def main():
    logger.info("Admin Bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Admin Bot to'xtatildi")
