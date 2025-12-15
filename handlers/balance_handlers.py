import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, LTC_ADDRESS, BTC_ADDRESS
from keyboards.main import get_main_keyboard
from states.deposit import DepositStates
from data.models import db

router = Router()

LTC_RATE = 0.013
BTC_RATE = 0.0000098





@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery, state: FSMContext):
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ]
    )
    
    balance_text = """Отличный выбор! А теперь введи сумму пополнения в USD.
Сумма может быть не менее 1 и не более 5000"""
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        balance_text,
        reply_markup=back_keyboard,
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_deposit_amount)


@router.message(DepositStates.waiting_for_deposit_amount)
async def receive_deposit_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.replace("$", "").replace(",", "").strip())
        if amount < 1 or amount > 5000:
            await message.answer("❌ Сумма должна быть от 1 до 5000 USD!\nВведите другую сумму:")
            return
    except ValueError:
        await message.answer("❌ Неверный формат!\nВведите число (например: 50):")
        return
    
    await state.update_data(amount_usd=amount)
    
    crypto_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💎 LTC", callback_data="select_ltc"),
                InlineKeyboardButton(text="₿ BTC", callback_data="select_btc")
            ],
            [
                InlineKeyboardButton(text="💳 UzCard", callback_data="select_uzcard"),
                InlineKeyboardButton(text="💳 Humo", callback_data="select_humo")
            ],
            [
                InlineKeyboardButton(text="🎁 Промокод", callback_data="promokod")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
            ]
        ]
    )
    
    await message.answer(
        f"💰 Сумма: <b>{amount} $</b>\n\nВыберите способ оплаты:",
        reply_markup=crypto_keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "select_ltc")
async def select_ltc(callback: CallbackQuery, state: FSMContext):
    await state.update_data(crypto_type="ltc", crypto_name="LTC")
    await show_crypto_confirmation(callback, state)


@router.callback_query(F.data == "select_btc")
async def select_btc(callback: CallbackQuery, state: FSMContext):
    await state.update_data(crypto_type="btc", crypto_name="BTC")
    await show_crypto_confirmation(callback, state)


@router.callback_query(F.data == "select_uzcard")
async def select_uzcard(callback: CallbackQuery):
    await callback.answer(
        "⚠️ UzCard временно недоступен.\nИспользуйте обменник: @BratskiyObmen",
        show_alert=True
    )


@router.callback_query(F.data == "select_humo")
async def select_humo(callback: CallbackQuery):
    await callback.answer(
        "⚠️ Humo временно недоступен.\nИспользуйте обменник: @BratskiyObmen",
        show_alert=True
    )


@router.callback_query(F.data == "promokod")
async def enter_promokod(callback: CallbackQuery, state: FSMContext):
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ]
    )
    await callback.message.edit_text(
        "🎁 <b>ПРОМОКОД</b>\n\nВведите ваш промокод:",
        reply_markup=back_keyboard,
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_amount)
    await state.update_data(is_promokod=True)


async def show_crypto_confirmation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount_usd = data.get("amount_usd", 0)
    crypto_type = data.get("crypto_type", "ltc")
    crypto_name = data.get("crypto_name", "LTC")
    
    application_id = random.randint(1000000, 9999999)
    
    if crypto_type == "ltc":
        crypto_amount = round(amount_usd * LTC_RATE, 4)
        pay_address = LTC_ADDRESS
    else:
        crypto_amount = round(amount_usd * BTC_RATE, 8)
        pay_address = BTC_ADDRESS
    
    await state.update_data(
        crypto_amount=crypto_amount,
        application_id=application_id,
        pay_address=pay_address
    )
    
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_crypto:{application_id}"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="back_to_main")
            ]
        ]
    )
    
    text = f"""https://t.me/bratskyobmen

<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{amount_usd} $</b>

👇 👇 👇
<b>Сумма к оплате: {crypto_amount} {crypto_name}</b>
☝️ ☝️ ☝️

⚠️⚠️⚠️ Необходимо перевести точную сумму для оплаты! ⚠️⚠️⚠️
После подтверждения заявки вы получите реквизиты для оплаты! У вас будет 30 минут для того, что бы оплатить. 
Вы можете отправлять сообщения оператору технической поддержки. 
stanislaw - Наш основной аккаунт оператора @BratskiyObmen был заблокирован Telegram. Наш новый аккаунт оператора: @BratskiyObmen

<i>Администрация магазина за действия обменников ответственности не несет!</i>"""
    
    await callback.message.edit_text(text, reply_markup=confirm_keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("confirm_crypto:"))
async def confirm_crypto_show_address(callback: CallbackQuery, state: FSMContext):
    application_id = callback.data.split(":")[1]
    data = await state.get_data()
    amount_usd = data.get("amount_usd", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    pay_address = data.get("pay_address", "")
    
    paid_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_crypto:{application_id}")
            ],
            [
                InlineKeyboardButton(text="✍️ Написать сообщение", url="https://t.me/BratskiyObmen")
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data="back_to_main")
            ]
        ]
    )
    
    text = f"""https://t.me/bratskyobmen

<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{amount_usd} $</b>

👇 👇 👇
<b>Сумма к оплате: {crypto_amount} {crypto_name}</b>

Реквизиты для оплаты: <code>{pay_address}</code>
☝️ ☝️ ☝️



⚠️⚠️⚠️ ПЕРЕВОДИТЬ НАДО ТОЧНУЮ СУММУ! ⚠️⚠️⚠️

Время для оплаты - 30 минут.
Если в течении 5 минут после оплаты ваш платеж не зачислился - отправьте ФОТО квитанции об оплате через кнопку "НАПИСАТЬ СООБЩЕНИЕ" ниже 👇.
stanislaw - Наш основной аккаунт оператора @BratskiyObmen был заблокирован Telegram. Наш новый аккаунт оператора: @BratskiyObmen

<i>Администрация магазина за действия обменников ответственности не несет!</i>"""
    
    await callback.message.edit_text(text, reply_markup=paid_keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("paid_crypto:"))
async def paid_crypto(callback: CallbackQuery, state: FSMContext):
    application_id = callback.data.split(":")[1]
    data = await state.get_data()
    amount_usd = data.get("amount_usd", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    
    await callback.message.edit_text(
        f"✅ <b>Заявка #{application_id} принята!</b>\n\n"
        f"💰 Сумма: {amount_usd} $\n\n"
        f"⏳ Ожидайте подтверждения от администратора.\n"
        f"Баланс будет пополнен после проверки.",
        parse_mode="HTML"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            admin_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_deposit:{callback.from_user.id}:{amount_usd}:{application_id}"),
                        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_deposit:{callback.from_user.id}:{application_id}")
                    ]
                ]
            )
            await callback.bot.send_message(
                admin_id,
                f"💰 <b>ПОЛЬЗОВАТЕЛЬ НАЖАЛ 'Я ОПЛАТИЛ'</b>\n\n"
                f"🆔 Заявка: #{application_id}\n"
                f"👤 Пользователь: {callback.from_user.full_name}\n"
                f"🆔 ID: <code>{callback.from_user.id}</code>\n"
                f"📱 Username: @{callback.from_user.username or 'Нет'}\n\n"
                f"💵 Сумма: {amount_usd} $\n"
                f"💎 Крипто: {crypto_amount} {crypto_name}",
                reply_markup=admin_keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Error sending admin message: {e}")
    
    await state.clear()


@router.message(DepositStates.waiting_for_amount)
async def receive_promokod(message: Message, state: FSMContext):
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
