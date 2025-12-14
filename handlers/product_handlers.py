import os
import random
import aiohttp
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, ADMIN_BOT_TOKEN, LTC_ADDRESS, BTC_ADDRESS
from keyboards.main import get_main_keyboard
from data.models import db
from data.products_data import PRODUCTS, DISTRICTS, LTC_RATE, BTC_RATE
from states.deposit import DepositStates

router = Router()


def get_products_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, product in PRODUCTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{product['name']} | {product['price_usd']}$",
                callback_data=f"select:{key}"
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

Выберите товар:
"""
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        products_text,
        reply_markup=get_products_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("select:"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    product_key = callback.data.replace("select:", "")
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
    
    await state.update_data(
        selected_product=product_key,
        selected_district=district_key,
        district_name=district_name
    )
    
    buy_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛒 Купить прикоп", callback_data=f"buy:delivery:{product_key}:{district_key}"),
            ],
            [
                InlineKeyboardButton(text="🛒 Купить магнит", callback_data=f"buy:pickup:{product_key}:{district_key}"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data=f"select:{product_key}")
            ]
        ]
    )
    
    text = f"""
<b>{product['name']}</b>
📍 Район: {district_name}

{product['description']}

💰 <b>Цена: {product['price_usd']} $</b>

Выберите способ получения:
"""
    
    await callback.message.edit_text(text, reply_markup=buy_keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("buy:"))
async def process_buy(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    
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
    
    await state.update_data(
        buy_type=buy_type,
        product_key=product_key,
        district_key=district_key,
        price=price
    )
    
    if not user or user.balance < price:
        current_balance = user.balance if user else 0
        needed = price - current_balance
        
        deposit_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💎 LTC", callback_data=f"deposit_crypto:ltc:{needed}"),
                    InlineKeyboardButton(text="🪙 BTC", callback_data=f"deposit_crypto:btc:{needed}")
                ],
                [
                    InlineKeyboardButton(text="🎁 ПРОМОКОД", callback_data="promokod")
                ],
                [
                    InlineKeyboardButton(text="🔙 Назад", callback_data=f"dist:{product_key}:{district_key}")
                ]
            ]
        )
        
        await callback.message.edit_text(
            f"❌ <b>У вас недостаточно баланса!</b>\n\n"
            f"💰 Ваш баланс: {current_balance} $\n"
            f"💵 Нужно: {price} $\n"
            f"📊 Не хватает: {needed} $\n\n"
            f"Выберите способ пополнения счета на сумму <b>{needed} $</b>:",
            reply_markup=deposit_keyboard,
            parse_mode="HTML"
        )
        return
    
    await complete_purchase(callback, state, product, district_name, buy_type)


async def complete_purchase(callback: CallbackQuery, state: FSMContext, product: dict, district_name: str, buy_type: str):
    user = db.get_user(callback.from_user.id)
    price = product['price_usd']
    
    order = db.create_order(
        user_id=callback.from_user.id,
        product_key=product['name'],
        product_name=product['name'],
        price=price
    )
    
    order_id = random.randint(1000000, 9999999)
    buy_type_text = "Доставка" if buy_type == "delivery" else "Самовывоз"
    
    success_text = f"""
✅ <b>Заявка #{order_id} подтверждена:</b>
{product['name']}, {district_name} (Ташкент)

«Store-Tashkent»™️
📦 ТОВАР: {product['name']}
📍 РАЙОН: {district_name}
🚚 ТИП: {buy_type_text}

Спасибо за покупку! 
Мы свяжемся с вами в ближайшее время.

Ваш новый баланс: {user.balance - price} $
"""
    
    db.update_balance(callback.from_user.id, -price)
    
    await callback.message.edit_text(success_text, parse_mode="HTML")
    
    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"🆕 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
                f"👤 Клиент: {callback.from_user.full_name}\n"
                f"🆔 ID: <code>{callback.from_user.id}</code>\n"
                f"📱 Username: @{callback.from_user.username or 'Нет'}\n\n"
                f"📦 Товар: {product['name']}\n"
                f"📍 Район: {district_name}\n"
                f"🚚 Тип: {buy_type_text}\n"
                f"💰 Сумма: {price} $",
                parse_mode="HTML"
            )
        except:
            pass
    
    await state.clear()


@router.callback_query(F.data.startswith("deposit_crypto:"))
async def deposit_crypto(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    
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
    
    await state.update_data(
        deposit_amount=amount_usd,
        crypto_type=crypto_type,
        crypto_name=crypto_name,
        crypto_amount=crypto_amount,
        application_id=application_id
    )
    
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_payment:{crypto_type}:{amount_usd}")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="products")
            ]
        ]
    )
    
    text = f"""
<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{amount_usd} $</b>

👇 👇 👇
<b>Сумма к оплате: {crypto_amount} {crypto_name}</b>
☝️ ☝️ ☝️

⚠️⚠️⚠️ Необходимо перевести точную сумму для оплаты! ⚠️⚠️⚠️
После подтверждения заявки вы получите реквизиты для оплаты! У вас будет 30 минут для того, что бы оплатить.
Вы можете отправлять сообщения оператору технической поддержки.

<b>stanislaw</b> - Наш основной аккаунт оператора @BratskiyObmen был заблокирован Telegram. Наш новый аккаунт оператора: @BratskiyObmen

Администрация магазина за действия обменников ответственности не несет!

https://t.me/BratskiyObmen
"""
    
    await callback.message.edit_text(text, reply_markup=confirm_keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("confirm_payment:"))
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    crypto_type = parts[1]
    amount_usd = int(parts[2])
    
    data = await state.get_data()
    application_id = data.get("application_id", random.randint(1000000, 9999999))
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    
    if crypto_type == "ltc":
        address = LTC_ADDRESS
        crypto_name = "LTC"
    else:
        address = BTC_ADDRESS
        crypto_name = "BTC"
    
    await state.update_data(address=address)
    
    payment_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Оплатил", callback_data="paid_confirm")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="products")
            ]
        ]
    )
    
    text = f"""
<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{amount_usd} $</b>

👇 👇 👇
<b>Сумма к оплате: {crypto_amount} {crypto_name}</b>
☝️ ☝️ ☝️

━━━━━━━━━━━━━━━━━━━━
<b>Адрес для оплаты:</b>
<code>{address}</code>
━━━━━━━━━━━━━━━━━━━━

<b>Заявка подтверждена</b>
Ожидайте назначения реквизитов. Время для оплаты - 30 минут.

@BratskiyObmen
https://t.me/BratskiyObmen
"""
    
    await callback.message.edit_text(text, reply_markup=payment_keyboard, parse_mode="HTML")


@router.callback_query(F.data == "paid_confirm")
async def paid_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id", 0)
    amount_usd = data.get("deposit_amount", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    address = data.get("address", "")
    
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_payment_info")
            ]
        ]
    )
    
    text = f"""
<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{amount_usd} $</b>

<b>Сумма к оплате: {crypto_amount} {crypto_name}</b>
<b>Реквизиты для оплаты:</b> <code>{address}</code>

<b>Напишите ваше сообщение</b>
<b>Как ускорить проверку платежа?</b>

1️⃣ Пришлите фото квитанции об оплате. ❗Именно квитанции, чаще всего в приложении банка есть кнопка "получить чек" "открыть квитанцию" и что-то такое. Далее необходимо сделать скриншот с экрана телефона или отправить файл PDF.
Отправка квитанции в PDF - значительно ускорит проверку.

2️⃣ В некоторых случаях необходимо видео-подтверждение вашей оплаты, как вы заходите в свое банковское приложение на телефоне и показать этот перевод. Видео необходимо отправить сюда в сообщения по заявке.
"""
    
    await callback.message.edit_text(text, reply_markup=back_keyboard, parse_mode="HTML")
    await state.set_state(DepositStates.waiting_for_screenshot)


@router.callback_query(F.data == "back_to_payment_info")
async def back_to_payment_info(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id", 0)
    amount_usd = data.get("deposit_amount", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    address = data.get("address", "")
    
    payment_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Оплатил", callback_data="paid_confirm")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="products")
            ]
        ]
    )
    
    text = f"""
<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{amount_usd} $</b>

👇 👇 👇
<b>Сумма к оплате: {crypto_amount} {crypto_name}</b>
☝️ ☝️ ☝️

━━━━━━━━━━━━━━━━━━━━
<b>Адрес для оплаты:</b>
<code>{address}</code>
━━━━━━━━━━━━━━━━━━━━

<b>Заявка подтверждена</b>
Ожидайте назначения реквизитов. Время для оплаты - 30 минут.
"""
    
    await state.clear()
    await callback.message.edit_text(text, reply_markup=payment_keyboard, parse_mode="HTML")


@router.callback_query(F.data == "send_payment_proof")
async def send_payment_proof(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📸 <b>Отправьте чек оплаты</b>\n\n"
        "Отправьте скриншот или ссылку на транзакцию:",
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_screenshot)


@router.message(DepositStates.waiting_for_screenshot)
async def receive_payment_proof(message: Message, state: FSMContext):
    data = await state.get_data()
    amount_usd = data.get("deposit_amount", 0)
    application_id = data.get("application_id", 0)
    crypto_name = data.get("crypto_name", "")
    crypto_amount = data.get("crypto_amount", 0)
    
    proof_text = ""
    photo_id = None
    
    if message.photo:
        photo_id = message.photo[-1].file_id
        proof_text = "📸 Скриншот"
    elif message.text:
        proof_text = message.text
    else:
        await message.answer("❌ Отправьте скриншот или текст!")
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 LTC QR 1", callback_data="show_qr:ltc:1"),
                InlineKeyboardButton(text="📱 LTC QR 2", callback_data="show_qr:ltc:2")
            ],
            [
                InlineKeyboardButton(text="✍️ Написать сообщение", callback_data="paid_confirm")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="products")
            ]
        ]
    )
    
    await message.answer(
        f"✅ <b>Заявка #{application_id} принята!</b>\n\n"
        f"💰 Сумма: {amount_usd} $\n"
        f"💎 Крипто: {crypto_amount} {crypto_name}\n\n"
        f"⏳ Ожидайте подтверждения администратора.\n"
        f"После проверки баланс будет пополнен.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    admin_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_deposit:{message.from_user.id}:{amount_usd}:{application_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_deposit:{message.from_user.id}:{application_id}")
            ]
        ]
    )
    
    admin_text = (
        f"💰 <b>НОВАЯ ЗАЯВКА НА ПОПОЛНЕНИЕ #{application_id}</b>\n\n"
        f"👤 Пользователь: {message.from_user.full_name}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"📱 Username: @{message.from_user.username or 'Нет'}\n\n"
        f"💵 Сумма: {amount_usd} $\n"
        f"💎 Крипто: {crypto_amount} {crypto_name}\n\n"
        f"📝 Доказательство: {proof_text}"
    )
    
    async with aiohttp.ClientSession() as session:
        if photo_id:
            for admin_id in ADMIN_IDS:
                try:
                    url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendPhoto"
                    
                    file_url = f"https://api.telegram.org/bot{message.bot.token}/getFile?file_id={photo_id}"
                    async with session.get(file_url) as resp:
                        file_data = await resp.json()
                        file_path = file_data.get("result", {}).get("file_path", "")
                    
                    if file_path:
                        download_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"
                        async with session.get(download_url) as resp:
                            photo_bytes = await resp.read()
                        
                        from aiohttp import FormData
                        form = FormData()
                        form.add_field('chat_id', str(admin_id))
                        form.add_field('caption', admin_text)
                        form.add_field('parse_mode', 'HTML')
                        form.add_field('photo', photo_bytes, filename='photo.jpg', content_type='image/jpeg')
                        form.add_field('reply_markup', str({
                            "inline_keyboard": [
                                [
                                    {"text": "✅ Подтвердить", "callback_data": f"confirm_deposit:{message.from_user.id}:{amount_usd}:{application_id}"},
                                    {"text": "❌ Отклонить", "callback_data": f"reject_deposit:{message.from_user.id}:{application_id}"}
                                ]
                            ]
                        }))
                        
                        await session.post(url, data=form)
                except Exception as e:
                    print(f"Error sending to admin: {e}")
        else:
            for admin_id in ADMIN_IDS:
                try:
                    url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": admin_id,
                        "text": admin_text,
                        "parse_mode": "HTML",
                        "reply_markup": {
                            "inline_keyboard": [
                                [
                                    {"text": "✅ Подтвердить", "callback_data": f"confirm_deposit:{message.from_user.id}:{amount_usd}:{application_id}"},
                                    {"text": "❌ Отклонить", "callback_data": f"reject_deposit:{message.from_user.id}:{application_id}"}
                                ]
                            ]
                        }
                    }
                    resp = await session.post(url, json=payload)
                    result = await resp.json()
                    print(f"Admin response: {result}")
                except Exception as e:
                    print(f"Error sending to admin: {e}")
    
    await state.clear()


@router.callback_query(F.data == "promokod")
async def enter_promokod(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎁 <b>ПРОМОКОД</b>\n\n"
        "Введите ваш промокод:",
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_amount)
    await state.update_data(is_promokod=True)


@router.message(DepositStates.waiting_for_amount)
async def check_promokod(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if data.get("is_promokod"):
        promokod = message.text.strip().upper()
        
        if promokod == "CHOY2024":
            amount = 50
            db.update_balance(message.from_user.id, amount)
            user = db.get_user(message.from_user.id)
            
            await message.answer(
                f"🎉 <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
                f"➕ Начислено: {amount} $\n"
                f"💰 Ваш баланс: {user.balance} $",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Промокод не найден или уже использован!",
                reply_markup=get_main_keyboard()
            )
        
        await state.clear()
