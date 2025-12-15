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
from states.deposit import DepositStates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# ===== MAHSULOTLAR - SHU YERDA O'ZGARTIRING =====
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
    }
}

DISTRICTS = {
    "chilonzor": "Чилонзор",
    "sergeli": "Сергели",
    "mirzoulugbek": "Мирзо Улугбек"
}

LTC_RATE = 0.013
BTC_RATE = 0.0000098
# ===== MAHSULOTLAR TUGADI =====

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())


def get_products_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, product in PRODUCTS.items():
        old_price = product.get('old_price_usd')
        if old_price:
            price_text = f"{product['name']} | {old_price}$ ➜ {product['price_usd']}$"
        else:
            price_text = f"{product['name']} | {product['price_usd']}$"
        buttons.append([
            InlineKeyboardButton(text=price_text, callback_data=f"select:{key}")
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_districts_keyboard(product_key: str) -> InlineKeyboardMarkup:
    buttons = []
    for key, name in DISTRICTS.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"dist:{product_key}:{key}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="products")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.callback_query(F.data == "products")
async def show_products(callback: CallbackQuery):
    logger.info(f"PRODUCTS: {len(PRODUCTS)} ta mahsulot")
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(
        "🛒 <b>КУПИТЬ ТОВАРЫ</b>\n\nВыберите товар:",
        reply_markup=get_products_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("select:"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    product_key = callback.data.replace("select:", "")
    product = PRODUCTS.get(product_key)
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    await state.update_data(selected_product=product_key)
    await callback.message.edit_text(
        f"✅ <b>Отличный выбор!</b>\nА теперь выбери район:",
        reply_markup=get_districts_keyboard(product_key),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("dist:"))
async def select_district(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    product_key = parts[1]
    district_key = parts[2]
    product = PRODUCTS.get(product_key)
    district_name = DISTRICTS.get(district_key, "")
    if not product:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    await state.update_data(selected_district=district_key, district_name=district_name)
    
    buy_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить прикоп", callback_data=f"buy:delivery:{product_key}:{district_key}")],
        [InlineKeyboardButton(text="🛒 Купить магнит", callback_data=f"buy:pickup:{product_key}:{district_key}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"select:{product_key}")]
    ])
    
    await callback.message.edit_text(
        f"<b>{product['name']}</b>\n📍 Район: {district_name}\n\n{product['description']}\n\n💰 <b>Цена: {product['price_usd']} $</b>\n\nВыберите способ получения:",
        reply_markup=buy_keyboard,
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("buy:"))
async def process_buy(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    buy_type = parts[1]
    product_key = parts[2]
    district_key = parts[3]
    product = PRODUCTS.get(product_key)
    district_name = DISTRICTS.get(district_key, "")
    if not product:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    user = db.get_user(callback.from_user.id)
    price = product['price_usd']
    await state.update_data(buy_type=buy_type, product_key=product_key, district_key=district_key, price=price)
    
    if not user or user.balance < price:
        current_balance = user.balance if user else 0
        needed = price - current_balance
        deposit_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 LTC", callback_data=f"deposit_crypto:ltc:{needed}"),
             InlineKeyboardButton(text="🪙 BTC", callback_data=f"deposit_crypto:btc:{needed}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"dist:{product_key}:{district_key}")]
        ])
        await callback.message.edit_text(
            f"❌ <b>У вас недостаточно баланса!</b>\n\n💰 Ваш баланс: {current_balance} $\n💵 Нужно: {price} $\n📊 Не хватает: {needed} $\n\nВыберите способ пополнения:",
            reply_markup=deposit_keyboard,
            parse_mode="HTML"
        )
        return
    
    # Xarid
    order_id = random.randint(1000000, 9999999)
    buy_type_text = "Доставка" if buy_type == "delivery" else "Самовывоз"
    db.update_balance(callback.from_user.id, -price)
    
    await callback.message.edit_text(
        f"✅ <b>Заявка #{order_id} подтверждена!</b>\n\n📦 ТОВАР: {product['name']}\n📍 РАЙОН: {district_name}\n🚚 ТИП: {buy_type_text}\n\n💰 Новый баланс: {user.balance - price} $",
        parse_mode="HTML"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id,
                f"🆕 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n👤 {callback.from_user.full_name}\n🆔 <code>{callback.from_user.id}</code>\n\n📦 {product['name']}\n📍 {district_name}\n🚚 {buy_type_text}\n💰 {price} $",
                parse_mode="HTML")
        except:
            pass
    await state.clear()


@dp.callback_query(F.data.startswith("deposit_crypto:"))
async def deposit_crypto(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    crypto_type = parts[1]
    amount_usd = int(parts[2])
    
    if crypto_type == "ltc":
        crypto_amount = round(amount_usd * LTC_RATE, 4)
        address = LTC_ADDRESS
        crypto_name = "LTC"
    else:
        crypto_amount = round(amount_usd * BTC_RATE, 8)
        address = BTC_ADDRESS
        crypto_name = "BTC"
    
    application_id = random.randint(1000000, 9999999)
    await state.update_data(deposit_amount=amount_usd, crypto_type=crypto_type, crypto_name=crypto_name, crypto_amount=crypto_amount, application_id=application_id)
    
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_crypto:{application_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="products")]
    ])
    
    await callback.message.edit_text(
        f"<b>Заявка #{application_id}</b>\nСпособ: {crypto_name}\nСумма: <b>{amount_usd} $</b>\n\n<b>К оплате: {crypto_amount} {crypto_name}</b>\n\n⚠️ Переводите точную сумму!",
        reply_markup=confirm_keyboard,
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("confirm_crypto:"))
async def confirm_crypto(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id")
    amount_usd = data.get("deposit_amount", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    crypto_type = data.get("crypto_type", "ltc")
    
    if crypto_type == "ltc":
        address = LTC_ADDRESS
    else:
        address = BTC_ADDRESS
    
    paid_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="products")]
    ])
    
    await state.update_data(address=address)
    await callback.message.edit_text(
        f"<b>Заявка #{application_id}</b>\n\n<b>К оплате: {crypto_amount} {crypto_name}</b>\n\n<b>Адрес:</b>\n<code>{address}</code>\n\n⏳ Время: 30 минут",
        reply_markup=paid_keyboard,
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "paid_confirm")
async def paid_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id", 0)
    amount_usd = data.get("deposit_amount", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    
    await callback.message.edit_text(
        f"✅ <b>Заявка #{application_id} принята!</b>\n\n💰 Сумма: {amount_usd} $\n\n⏳ Ожидайте подтверждения.",
        parse_mode="HTML"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            admin_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_deposit:{callback.from_user.id}:{amount_usd}:{application_id}"),
                 InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_deposit:{callback.from_user.id}:{application_id}")]
            ])
            await bot.send_message(admin_id,
                f"💰 <b>ЗАЯВКА #{application_id}</b>\n\n👤 {callback.from_user.full_name}\n🆔 <code>{callback.from_user.id}</code>\n\n💵 {amount_usd} $\n💎 {crypto_amount} {crypto_name}",
                reply_markup=admin_kb,
                parse_mode="HTML")
        except:
            pass
    await state.clear()


@dp.callback_query(F.data.startswith("confirm_deposit:"))
async def handle_confirm_deposit(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[1])
    amount = int(parts[2])
    application_id = parts[3]
    db.update_balance(user_id, amount)
    user = db.get_user(user_id)
    await callback.message.edit_text(f"✅ <b>ЗАЯВКА #{application_id} ПОДТВЕРЖДЕНА</b>\n\n💵 Зачислено: {amount} $", parse_mode="HTML")
    try:
        await bot.send_message(user_id, f"✅ <b>БАЛАНС ПОПОЛНЕН!</b>\n\n💰 Зачислено: {amount} $\n💵 Баланс: {user.balance} $", parse_mode="HTML")
    except:
        pass


@dp.callback_query(F.data.startswith("reject_deposit:"))
async def handle_reject_deposit(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[1])
    application_id = parts[2]
    await callback.message.edit_text(f"❌ <b>ЗАЯВКА #{application_id} ОТКЛОНЕНА</b>", parse_mode="HTML")
    try:
        await bot.send_message(user_id, f"❌ <b>Заявка #{application_id} отклонена</b>", parse_mode="HTML")
    except:
        pass


async def main():
    from handlers import main_router, balance_router, support_router
    
    # product_router NI OLIB TASHLADIM - hamma narsa shu faylda
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
