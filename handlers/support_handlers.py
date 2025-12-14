from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards.support import get_support_keyboard, get_faq_keyboard, get_cancel_keyboard
from keyboards.main import get_main_keyboard, get_back_to_main_keyboard
from states.deposit import SupportStates

router = Router()


@router.callback_query(F.data == "support")
async def show_support(callback: CallbackQuery):
    support_text = """
🧾 <b>ПОДДЕРЖКА</b>

━━━━━━━━━━━━━━━━━━━━
Есть вопросы? Мы поможем!

🕐 Время работы: 09:00 - 21:00
📱 Время ответа: 5-30 минут
━━━━━━━━━━━━━━━━━━━━

Выберите действие:
"""
    
    await callback.message.edit_text(
        support_text,
        reply_markup=get_support_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "write_support")
async def start_support_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💬 <b>НАПИСАТЬ ОПЕРАТОРУ</b>\n\n"
        "Опишите вашу проблему или вопрос.\n"
        "Мы ответим как можно скорее!",
        parse_mode="HTML"
    )
    await state.set_state(SupportStates.waiting_for_message)


@router.message(SupportStates.waiting_for_message)
async def receive_support_message(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "❌ Отменено",
            reply_markup=get_main_keyboard()
        )
        return
    
    await message.answer(
        "✅ <b>СООБЩЕНИЕ ОТПРАВЛЕНО!</b>\n\n"
        "Операторы ответят вам в ближайшее время.\n"
        "Спасибо за обращение! 🙏",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"📨 <b>НОВОЕ ОБРАЩЕНИЕ!</b>\n\n"
                f"👤 Пользователь: {message.from_user.full_name}\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n"
                f"📱 Username: @{message.from_user.username or 'Нет'}\n\n"
                f"💬 <b>Сообщение:</b>\n{message.text}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await state.clear()


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery):
    faq_text = """
❓ <b>ЧАСТЫЕ ВОПРОСЫ</b>

Выберите тему:
"""
    
    await callback.message.edit_text(
        faq_text,
        reply_markup=get_faq_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "faq_delivery")
async def faq_delivery(callback: CallbackQuery):
    text = """
🚚 <b>ДОСТАВКА</b>

━━━━━━━━━━━━━━━━━━━━
📍 <b>Ташкент:</b>
• Доставка: 1-2 дня
• Стоимость: от 15,000 сум

📍 <b>Регионы:</b>
• Доставка: 3-5 дней
• Стоимость: от 25,000 сум

⏰ <b>Время работы:</b>
Пн-Сб: 09:00 - 21:00
Вс: Выходной

📦 Отслеживание заказа в разделе "Профиль"
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_faq_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "faq_payment")
async def faq_payment(callback: CallbackQuery):
    text = """
💳 <b>СПОСОБЫ ОПЛАТЫ</b>

━━━━━━━━━━━━━━━━━━━━
💎 <b>Криптовалюта:</b>
• LTC (Litecoin)
• BTC (Bitcoin)

💳 <b>Карты:</b>
• Uzcard
• Humo
• Visa/Mastercard

🎁 <b>Промокоды:</b>
• Получайте от партнеров
• Активируйте в разделе "Баланс"

⏱ Проверка платежа: до 30 минут
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_faq_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "faq_return")
async def faq_return(callback: CallbackQuery):
    text = """
🔄 <b>ВОЗВРАТ</b>

━━━━━━━━━━━━━━━━━━━━
✅ <b>Возврат возможен если:</b>
• Товар поврежден
• Неправильный товар
• Просроченный товар

❌ <b>Возврат невозможен:</b>
• Вскрытая упаковка
• Прошло более 3 дней

📋 <b>Порядок возврата:</b>
1. Свяжитесь с поддержкой
2. Отправьте фото/видео
3. Ожидайте решения (24 часа)

💰 Деньги возвращаются на баланс
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_faq_keyboard(),
        parse_mode="HTML"
    )
