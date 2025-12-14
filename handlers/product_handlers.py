import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards.main import get_main_keyboard
from data.models import db
from data.products_data import PRODUCTS, DISTRICTS, LTC_RATE

router = Router()


def get_products_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, product in PRODUCTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{product['name']} | {product['price_usd']}$",
                callback_data=f"select_{key}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_districts_keyboard(product_key: str) -> InlineKeyboardMarkup:
    buttons = []
    for key, name in DISTRICTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"dist:{product_key}:{key}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="products")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "products")
async def show_products(callback: CallbackQuery):
    products_text = """
🛒 <b>КУПИТЬ ТОВАРЫ</b>

━━━━━━━━━━━━━━━━━━━━
Выберите товар:
━━━━━━━━━━━━━━━━━━━━
"""
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(
        products_text,
        reply_markup=get_products_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("select_"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    product_key = callback.data.replace("select_", "")
    product = PRODUCTS.get(product_key)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    await state.update_data(selected_product=product_key)
    
    district_text = f"""
✅ <b>Отличный выбор!</b>
А теперь выбери район:
"""
    
    await callback.message.edit_text(
        district_text,
        reply_markup=get_districts_keyboard(product_key),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("dist:"))
async def select_district(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    
    product_key = parts[1]
    district_key = parts[2]
    
    product = PRODUCTS.get(product_key)
    district_name = DISTRICTS.get(district_key, "")
    
    if not product or not district_name:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    user = db.get_user(callback.from_user.id)
    user_balance_usd = 0
    user_balance_ltc = 0.0
    
    if user:
        user_balance_usd = user.balance
        user_balance_ltc = round(user.balance * LTC_RATE, 4)
    
    district_display = district_name
    
    product_text = f"""
<b>{product['name']}</b> (Ташкент, {district_display})

{product['description']}

<b>Цена: {product['price_usd']} $</b>

У вас нет персональной скидки! Покупайте в магазине и получайте скидку для постоянных клиентов

<b>Твой баланс: {user_balance_usd} $ ({user_balance_ltc} LTC)</b>
"""
    
    payment_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💳 Оплатить {product['price_usd']}$",
                    url=product['payment_url']
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Я оплатил",
                    callback_data=f"paid:{product_key}:{district_key}"
                )
            ],
            [
                InlineKeyboardButton(text="🔙 К товарам", callback_data="products")
            ]
        ]
    )
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    image_path = product.get('photo')
    if image_path and os.path.exists(image_path):
        try:
            photo = FSInputFile(image_path)
            await callback.message.answer_photo(
                photo=photo,
                caption=product_text,
                reply_markup=payment_keyboard,
                parse_mode="HTML"
            )
            return
        except Exception:
            pass
    
    await callback.message.answer(
        product_text,
        reply_markup=payment_keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("paid:"))
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    
    product_key = parts[1]
    district_key = parts[2]
    
    product = PRODUCTS.get(product_key)
    district_name = DISTRICTS.get(district_key, "")
    
    if not product:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    district_display = district_name
    
    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"💰 <b>НОВЫЙ ЗАКАЗ - ОЖИДАЕТ ПРОВЕРКИ!</b>\n\n"
                f"👤 Клиент: {callback.from_user.full_name}\n"
                f"🆔 ID: <code>{callback.from_user.id}</code>\n"
                f"📱 Username: @{callback.from_user.username or 'Нет'}\n\n"
                f"📦 Товар: {product['name']}\n"
                f"📍 Район: {district_display}\n"
                f"💵 Сумма: {product['price_usd']}$\n\n"
                f"🔗 Payment URL: {product['payment_url']}\n\n"
                f"Проверьте оплату в NOWPayments!",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await callback.message.edit_caption(
        caption=(
            "✅ <b>ЗАЯВКА ПРИНЯТА!</b>\n\n"
            f"📦 Товар: {product['name']}\n"
            f"📍 Район: {district_display}\n"
            f"💵 Сумма: {product['price_usd']}$\n\n"
            "⏳ Ожидайте проверки оплаты.\n"
            "После подтверждения вы получите адрес!"
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ]
        ),
        parse_mode="HTML"
    )
    
    await state.clear()
