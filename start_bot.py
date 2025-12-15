#!/usr/bin/env python3
"""
BU BOTNI ISHGA TUSHIRISH UCHUN FAQAT SHU FAYLNI ISHLATING:
python start_bot.py
"""
import asyncio
import logging
import sys
import random
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, BufferedInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [7149917323]  # Admin ID
LTC_ADDRESS = os.getenv("LTC_ADDRESS", "ltc1qxyz...")
BTC_ADDRESS = os.getenv("BTC_ADDRESS", "bc1qxyz...")

# Agar .env dan yuklash kerak bo'lsa
try:
    from config import BOT_TOKEN, ADMIN_IDS, LTC_ADDRESS, BTC_ADDRESS
except:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ============== MAHSULOTLAR ==============
PRODUCTS = {
    "coco_120": {
        "name": "🍫Euro Hash | 0.5g",
        "price_usd": 19,
        "old_price_usd": 21,
        "description": "💯Лучший в своем деле💯\n\nЛюбишь когда тебя убивает?☠️\nEuro Hash сможет это сделать с одной плюшки😏"
    },
    "coco_200": {
        "name": "🍫Euro Hash | 1g",
        "price_usd": 42,
        "old_price_usd": None,
        "description": "💯Лучший в своем деле💯\n\nЛюбишь когда тебя убивает?☠️\nEuro Hash сможет это сделать с одной плюшки😏"
    },
    "euro_hash_05": {
        "name": "🍫Euro Hash | 0.5g",
        "price_usd": 19,
        "old_price_usd": 21,
        "description": "💯Лучший в своем деле💯\n\nЛюбишь когда тебя убивает?☠️\nEuro Hash сможет это сделать с одной плюшки😏"
    },
    "euro_hash_1": {
        "name": "🍫Euro Hash | 1g",
        "price_usd": 42,
        "old_price_usd": None,
        "description": "💯Лучший в своем деле💯\n\nЛюбишь когда тебя убивает?☠️\nEuro Hash сможет это сделать с одной плюшки😏"
    },
    "euro_hash_3": {
        "name": "🍫Euro Hash | 3g",
        "price_usd": 90,
        "old_price_usd": 102,
        "description": "💯Лучший в своем деле💯\n\nЛюбишь когда тебя убивает?☠️\nEuro Hash сможет это сделать с одной плюшки😏"
    }
}

DISTRICTS = {
    "chilonzor": "Чилонзор",
    "sergeli": "Сергели",
    "mirzoulugbek": "Мирзо Улугбек"
}

LTC_RATE = 0.013
BTC_RATE = 0.0000098
# ============== MAHSULOTLAR TUGADI ==============

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Database import
try:
    from data.models import db
except:
    db = None


def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить Товары", callback_data="products"),
         InlineKeyboardButton(text="💳 Пополнить Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="⚠️ Правила", callback_data="rules"),
         InlineKeyboardButton(text="⭐️ Отзывы", callback_data="reviews")],
        [InlineKeyboardButton(text="🧾 Поддержка", url="https://t.me/StoreTashkent_support"),
         InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]
    ])


def get_products_keyboard():
    buttons = []
    for key, product in PRODUCTS.items():
        old_price = product.get('old_price_usd')
        if old_price:
            price_text = f"{product['name']} | {old_price}$ ➜ {product['price_usd']}$"
        else:
            price_text = f"{product['name']} | {product['price_usd']}$"
        buttons.append([InlineKeyboardButton(text=price_text, callback_data=f"select:{key}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_districts_keyboard(product_key):
    buttons = []
    for key, name in DISTRICTS.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"dist:{product_key}:{key}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="products")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"START: {message.from_user.id}")
    if db:
        user = db.get_user(message.from_user.id)
        if not user:
            db.create_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    await message.answer(
        f"Добро пожаловать!\n\n<b>Твой баланс:</b> 0 USD",
        reply_markup=get_main_keyboard()
    )


@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())


@dp.callback_query(F.data == "products")
async def show_products(callback: CallbackQuery):
    logger.info(f"===== PRODUCTS BOSILDI! {len(PRODUCTS)} ta mahsulot =====")
    print(f"\n\n===== PRODUCTS: {len(PRODUCTS)} ta =====\n\n")
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        "🛒 <b>КУПИТЬ ТОВАРЫ</b>\n\nВыберите товар:",
        reply_markup=get_products_keyboard()
    )


@dp.callback_query(F.data.startswith("select:"))
async def select_product(callback: CallbackQuery):
    product_key = callback.data.replace("select:", "")
    product = PRODUCTS.get(product_key)
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"✅ <b>Отличный выбор!</b>\nА теперь выбери район:",
        reply_markup=get_districts_keyboard(product_key)
    )


@dp.callback_query(F.data.startswith("dist:"))
async def select_district(callback: CallbackQuery):
    parts = callback.data.split(":")
    product_key = parts[1]
    district_key = parts[2]
    product = PRODUCTS.get(product_key)
    district_name = DISTRICTS.get(district_key, "")
    
    if not product:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    buy_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить прикоп", callback_data=f"buy:delivery:{product_key}:{district_key}")],
        [InlineKeyboardButton(text="🛒 Купить магнит", callback_data=f"buy:pickup:{product_key}:{district_key}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"select:{product_key}")]
    ])
    
    await callback.message.edit_text(
        f"<b>{product['name']}</b>\n📍 Район: {district_name}\n\n{product['description']}\n\n💰 <b>Цена: {product['price_usd']} $</b>",
        reply_markup=buy_keyboard
    )


@dp.callback_query(F.data.startswith("buy:"))
async def process_buy(callback: CallbackQuery):
    parts = callback.data.split(":")
    buy_type = parts[1]
    product_key = parts[2]
    district_key = parts[3]
    product = PRODUCTS.get(product_key)
    district_name = DISTRICTS.get(district_key, "")
    
    if not product:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    price = product['price_usd']
    user_balance = 0
    if db:
        user = db.get_user(callback.from_user.id)
        user_balance = user.balance if user else 0
    
    if user_balance < price:
        needed = price - user_balance
        deposit_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 LTC", callback_data=f"deposit:ltc:{needed}"),
             InlineKeyboardButton(text="🪙 BTC", callback_data=f"deposit:btc:{needed}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"dist:{product_key}:{district_key}")]
        ])
        await callback.message.edit_text(
            f"❌ <b>У вас недостаточно баланса!</b>\n\n💰 Баланс: {user_balance} $\n💵 Нужно: {price} $\n📊 Не хватает: {needed} $",
            reply_markup=deposit_keyboard
        )
        return
    
    # Xarid
    order_id = random.randint(1000000, 9999999)
    buy_type_text = "Доставка" if buy_type == "delivery" else "Самовывоз"
    if db:
        db.update_balance(callback.from_user.id, -price)
    
    await callback.message.edit_text(
        f"✅ <b>Заявка #{order_id} подтверждена!</b>\n\n📦 {product['name']}\n📍 {district_name}\n🚚 {buy_type_text}\n\n💰 Новый баланс: {user_balance - price} $"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id,
                f"🆕 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n👤 {callback.from_user.full_name}\n🆔 <code>{callback.from_user.id}</code>\n\n📦 {product['name']}\n📍 {district_name}\n🚚 {buy_type_text}\n💰 {price} $")
        except:
            pass


@dp.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    await callback.message.edit_text(
        "Введите сумму пополнения (от 1 до 5000 USD):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ])
    )


@dp.callback_query(F.data == "rules")
async def show_rules(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚠️ <b>ПРАВИЛА</b>\n\nhttps://telegra.ph/Pravila-Magazina-08-10",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ])
    )


@dp.callback_query(F.data == "reviews")
async def show_reviews(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐️ <b>ОТЗЫВЫ</b>\n\n👤 Алексей: \"Отличный чай!\" ⭐⭐⭐⭐⭐",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ])
    )


@dp.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_balance = 0
    if db:
        user = db.get_user(callback.from_user.id)
        user_balance = user.balance if user else 0
    
    await callback.message.edit_text(
        f"👤 <b>ПРОФИЛЬ</b>\n\n🆔 ID: <code>{callback.from_user.id}</code>\n💰 Баланс: {user_balance} $",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ])
    )


async def main():
    logger.info(f"Bot ishga tushdi! {len(PRODUCTS)} ta mahsulot mavjud")
    print(f"\n=== BOT ISHGA TUSHDI ===")
    print(f"=== MAHSULOTLAR: {len(PRODUCTS)} ta ===")
    for k, v in PRODUCTS.items():
        print(f"  - {v['name']}")
    print(f"========================\n")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
