import uuid
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import PAYMENT_CARD, PAYMENT_CARD_HOLDER, ADMIN_IDS
from keyboards.balance import get_balance_keyboard, get_card_amounts_keyboard, get_payment_confirm_keyboard
from keyboards.main import get_main_keyboard
from states.deposit import DepositStates
from data.models import db
from utils import nowpayments

router = Router()

USD_TO_UZS = 12800
LTC_RATE = 0.013
BTC_RATE = 0.0000098

SUPPORT_USERNAME = "@UZBobmennikTosh"


@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    balance = user.balance if user else 0
    
    balance_text = f"""
💳 <b>ПОПОЛНЕНИЕ БАЛАНСА</b>

━━━━━━━━━━━━━━━━━━━━
💰 Ваш баланс: <b>{balance} $</b>
━━━━━━━━━━━━━━━━━━━━

Выберите способ оплаты:
"""
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        balance_text,
        reply_markup=get_balance_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "pay_ltc")
async def pay_ltc(callback: CallbackQuery, state: FSMContext):
    await state.update_data(crypto_type="ltc", crypto_name="LTC")
    await show_amount_selection(callback, "LTC")


@router.callback_query(F.data == "pay_btc")
async def pay_btc(callback: CallbackQuery, state: FSMContext):
    await state.update_data(crypto_type="btc", crypto_name="BTC")
    await show_amount_selection(callback, "BTC")


async def show_amount_selection(callback: CallbackQuery, crypto_name: str):
    amounts_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💵 50 $", callback_data="crypto_50"),
                InlineKeyboardButton(text="💵 100 $", callback_data="crypto_100")
            ],
            [
                InlineKeyboardButton(text="💵 200 $", callback_data="crypto_200"),
                InlineKeyboardButton(text="💵 500 $", callback_data="crypto_500")
            ],
            [
                InlineKeyboardButton(text="💵 Другая сумма", callback_data="crypto_custom")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="balance")
            ]
        ]
    )
    
    await callback.message.edit_text(
        f"💎 <b>ПОПОЛНЕНИЕ {crypto_name}</b>\n\n"
        f"Выберите сумму пополнения:",
        reply_markup=amounts_keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("crypto_"))
async def process_crypto_amount(callback: CallbackQuery, state: FSMContext):
    amount_str = callback.data.replace("crypto_", "")
    data = await state.get_data()
    crypto_type = data.get("crypto_type", "ltc")
    crypto_name = data.get("crypto_name", "LTC")
    
    if amount_str == "custom":
        await callback.message.edit_text(
            "💵 <b>ДРУГАЯ СУММА</b>\n\n"
            "Введите сумму в долларах (минимум 10$):",
            parse_mode="HTML"
        )
        await state.set_state(DepositStates.waiting_for_crypto_amount)
        return
    
    try:
        amount_usd = int(amount_str)
    except ValueError:
        return
    
    await show_payment_confirmation(callback, state, amount_usd, crypto_type, crypto_name)


@router.message(DepositStates.waiting_for_crypto_amount)
async def receive_crypto_amount(message: Message, state: FSMContext):
    try:
        amount_usd = int(message.text.replace("$", "").replace(",", "").strip())
        if amount_usd < 10:
            await message.answer("❌ Минимальная сумма 10$!\nВведите другую сумму:")
            return
    except ValueError:
        await message.answer("❌ Неверный формат!\nВведите число (например: 50):")
        return
    
    data = await state.get_data()
    crypto_type = data.get("crypto_type", "ltc")
    crypto_name = data.get("crypto_name", "LTC")
    
    await state.clear()
    await state.update_data(crypto_type=crypto_type, crypto_name=crypto_name)
    
    application_id = random.randint(1000000, 9999999)
    
    if crypto_type == "ltc":
        crypto_amount = round(amount_usd * LTC_RATE, 4)
    else:
        crypto_amount = round(amount_usd * BTC_RATE, 8)
    
    await state.update_data(
        amount_usd=amount_usd,
        crypto_amount=crypto_amount,
        application_id=application_id
    )
    
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_crypto_payment")
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data="balance")
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

После подтверждения заявки вы получите реквизиты для оплаты! 
У вас будет <b>30 минут</b> для того, чтобы оплатить.

Вы можете отправлять сообщения оператору технической поддержки.
{SUPPORT_USERNAME}
"""
    
    await message.answer(text, reply_markup=confirm_keyboard, parse_mode="HTML")


async def show_payment_confirmation(callback: CallbackQuery, state: FSMContext, amount_usd: int, crypto_type: str, crypto_name: str):
    application_id = random.randint(1000000, 9999999)
    
    if crypto_type == "ltc":
        crypto_amount = round(amount_usd * LTC_RATE, 4)
    else:
        crypto_amount = round(amount_usd * BTC_RATE, 8)
    
    await state.update_data(
        amount_usd=amount_usd,
        crypto_amount=crypto_amount,
        application_id=application_id
    )
    
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_crypto_payment")
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data="balance")
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

После подтверждения заявки вы получите реквизиты для оплаты! 
У вас будет <b>30 минут</b> для того, чтобы оплатить.

Вы можете отправлять сообщения оператору технической поддержки.
{SUPPORT_USERNAME}
"""
    
    await callback.message.edit_text(text, reply_markup=confirm_keyboard, parse_mode="HTML")


@router.callback_query(F.data == "confirm_crypto_payment")
async def confirm_crypto_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount_usd = data.get("amount_usd", 0)
    crypto_type = data.get("crypto_type", "ltc")
    crypto_name = data.get("crypto_name", "LTC")
    crypto_amount = data.get("crypto_amount", 0)
    application_id = data.get("application_id", 0)
    
    await callback.message.edit_text("⏳ Создаем платеж...")
    
    order_id = f"user_{callback.from_user.id}_{application_id}"
    
    payment = await nowpayments.create_payment(
        amount_usd=amount_usd,
        currency=crypto_type,
        order_id=order_id,
        order_description=f"Balance top-up {amount_usd}$ for user {callback.from_user.id}"
    )
    
    if payment and payment.get("pay_address"):
        pay_address = payment["pay_address"]
        pay_amount = payment.get("pay_amount", crypto_amount)
        payment_id = payment.get("payment_id", "")
        
        await state.update_data(payment_id=payment_id, pay_address=pay_address)
        
        paid_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_crypto:{payment_id}")
                ],
                [
                    InlineKeyboardButton(text="❌ Отменить", callback_data="balance")
                ]
            ]
        )
        
        text = f"""
<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{amount_usd} $</b>

━━━━━━━━━━━━━━━━━━━━
<b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:</b>

Адрес {crypto_name}:
<code>{pay_address}</code>

Сумма: <b>{pay_amount} {crypto_name}</b>
━━━━━━━━━━━━━━━━━━━━

⚠️ Переведите <b>ТОЧНУЮ</b> сумму на указанный адрес!
⏳ У вас есть <b>30 минут</b> на оплату.

После оплаты нажмите кнопку "Я оплатил"
"""
        
        await callback.message.edit_text(text, reply_markup=paid_keyboard, parse_mode="HTML")
        
        for admin_id in ADMIN_IDS:
            try:
                await callback.bot.send_message(
                    admin_id,
                    f"💰 <b>НОВАЯ ЗАЯВКА НА ПОПОЛНЕНИЕ</b>\n\n"
                    f"🆔 Заявка: #{application_id}\n"
                    f"👤 Пользователь: {callback.from_user.full_name}\n"
                    f"🆔 ID: <code>{callback.from_user.id}</code>\n"
                    f"📱 Username: @{callback.from_user.username or 'Нет'}\n\n"
                    f"💵 Сумма: {amount_usd} $\n"
                    f"💎 Крипто: {pay_amount} {crypto_name}\n"
                    f"📍 Адрес: <code>{pay_address}</code>\n"
                    f"🔗 Payment ID: <code>{payment_id}</code>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    else:
        await callback.message.edit_text(
            "❌ Ошибка при создании платежа.\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=get_balance_keyboard()
        )


@router.callback_query(F.data.startswith("check_crypto:"))
async def check_crypto_payment(callback: CallbackQuery, state: FSMContext):
    payment_id = callback.data.replace("check_crypto:", "")
    
    data = await state.get_data()
    amount_usd = data.get("amount_usd", 0)
    application_id = data.get("application_id", 0)
    
    await callback.answer("⏳ Проверяем статус платежа...")
    
    status = await nowpayments.get_payment_status(payment_id)
    
    if status:
        payment_status = status.get("payment_status", "")
        
        if payment_status in ["finished", "confirmed"]:
            db.update_balance(callback.from_user.id, amount_usd)
            user = db.get_user(callback.from_user.id)
            
            await callback.message.edit_text(
                f"✅ <b>ОПЛАТА ПОДТВЕРЖДЕНА!</b>\n\n"
                f"💰 Зачислено: {amount_usd} $\n"
                f"💵 Ваш баланс: {user.balance} $\n\n"
                f"Спасибо за пополнение! 🙏",
                parse_mode="HTML"
            )
            
            for admin_id in ADMIN_IDS:
                try:
                    await callback.bot.send_message(
                        admin_id,
                        f"✅ <b>ОПЛАТА ПОДТВЕРЖДЕНА</b>\n\n"
                        f"🆔 Заявка: #{application_id}\n"
                        f"👤 Пользователь: {callback.from_user.full_name}\n"
                        f"💵 Сумма: {amount_usd} $\n"
                        f"🔗 Payment ID: {payment_id}",
                        parse_mode="HTML"
                    )
                except:
                    pass
            
            await state.clear()
        
        elif payment_status == "waiting":
            await callback.answer(
                "⏳ Ожидаем поступление средств...\n"
                "Попробуйте проверить позже.",
                show_alert=True
            )
        
        elif payment_status == "confirming":
            await callback.answer(
                "⏳ Платеж обрабатывается...\n"
                "Подождите несколько минут.",
                show_alert=True
            )
        
        elif payment_status == "expired":
            await callback.message.edit_text(
                "❌ <b>ВРЕМЯ ИСТЕКЛО</b>\n\n"
                "Платеж не был получен в течение 30 минут.\n"
                "Создайте новую заявку.",
                reply_markup=get_balance_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
        
        else:
            for admin_id in ADMIN_IDS:
                try:
                    await callback.bot.send_message(
                        admin_id,
                        f"❓ <b>ПРОВЕРКА ПЛАТЕЖА</b>\n\n"
                        f"👤 Пользователь: {callback.from_user.full_name}\n"
                        f"🆔 ID: <code>{callback.from_user.id}</code>\n"
                        f"💵 Сумма: {amount_usd} $\n"
                        f"🔗 Payment ID: <code>{payment_id}</code>\n"
                        f"📊 Статус: {payment_status}\n\n"
                        f"Для ручного подтверждения:\n"
                        f"<code>/add_balance {callback.from_user.id} {amount_usd}</code>",
                        parse_mode="HTML"
                    )
                except:
                    pass
            
            await callback.answer(
                "📨 Заявка отправлена оператору.\n"
                "Мы проверим и подтвердим вручную.",
                show_alert=True
            )
    else:
        await callback.answer(
            "❌ Не удалось проверить статус.\n"
            "Попробуйте позже или обратитесь в поддержку.",
            show_alert=True
        )


@router.callback_query(F.data == "promokod")
async def enter_promokod(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎁 <b>ПРОМОКОД</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Введите ваш промокод:",
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_amount)
    await state.update_data(is_promokod=True)


@router.callback_query(F.data == "pay_card")
async def pay_card(callback: CallbackQuery):
    await callback.message.edit_text(
        "💳 <b>ОПЛАТА КАРТОЙ</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Выберите сумму пополнения:",
        reply_markup=get_card_amounts_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("amount_"))
async def select_amount(callback: CallbackQuery, state: FSMContext):
    amount_str = callback.data.replace("amount_", "")
    
    if amount_str == "custom":
        await callback.message.edit_text(
            "💵 <b>ДРУГАЯ СУММА</b>\n\n"
            "Введите сумму пополнения (в долларах):",
            parse_mode="HTML"
        )
        await state.set_state(DepositStates.waiting_for_amount)
        return
    
    try:
        amount = int(amount_str)
    except ValueError:
        return
    
    await state.update_data(deposit_amount=amount)
    
    payment_text = f"""
💳 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ</b>

━━━━━━━━━━━━━━━━━━━━
💰 Сумма: <b>{amount} $</b>
━━━━━━━━━━━━━━━━━━━━

📌 <b>Переведите на карту:</b>

💳 <code>{PAYMENT_CARD}</code>
👤 {PAYMENT_CARD_HOLDER}

━━━━━━━━━━━━━━━━━━━━
📸 После оплаты отправьте скриншот чека!

⚠️ <i>Проверка занимает до 30 минут</i>
"""
    
    await callback.message.edit_text(
        payment_text,
        reply_markup=get_payment_confirm_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_screenshot)


@router.message(DepositStates.waiting_for_amount)
async def receive_amount(message: Message, state: FSMContext):
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
        return
    
    try:
        amount = int(message.text.replace(",", "").replace(" ", "").replace("$", ""))
        if amount < 10:
            await message.answer(
                "❌ Минимальная сумма 10$!\n"
                "Введите другую сумму:"
            )
            return
    except ValueError:
        await message.answer(
            "❌ Неверный формат!\n"
            "Введите только число:"
        )
        return
    
    await state.update_data(deposit_amount=amount)
    
    payment_text = f"""
💳 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ</b>

━━━━━━━━━━━━━━━━━━━━
💰 Сумма: <b>{amount} $</b>
━━━━━━━━━━━━━━━━━━━━

📌 <b>Переведите на карту:</b>

💳 <code>{PAYMENT_CARD}</code>
👤 {PAYMENT_CARD_HOLDER}

━━━━━━━━━━━━━━━━━━━━
📸 После оплаты отправьте скриншот чека!

⚠️ <i>Проверка занимает до 30 минут</i>
"""
    
    await message.answer(payment_text, parse_mode="HTML")
    await state.set_state(DepositStates.waiting_for_screenshot)


@router.message(DepositStates.waiting_for_screenshot, F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("deposit_amount", 0)
    
    await message.answer(
        f"✅ <b>ЧЕК ПРИНЯТ!</b>\n\n"
        f"💰 Сумма: {amount} $\n\n"
        f"⏳ Ожидайте проверки администратором.\n"
        f"Баланс будет пополнен после подтверждения.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(
                admin_id,
                photo=message.photo[-1].file_id,
                caption=f"💰 <b>НОВАЯ ОПЛАТА КАРТОЙ!</b>\n\n"
                       f"👤 Пользователь: {message.from_user.full_name}\n"
                       f"🆔 ID: <code>{message.from_user.id}</code>\n"
                       f"📱 Username: @{message.from_user.username or 'Нет'}\n\n"
                       f"💵 Сумма: {amount} $\n\n"
                       f"Для подтверждения:\n"
                       f"<code>/add_balance {message.from_user.id} {amount}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await state.clear()
