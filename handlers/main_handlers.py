from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import os

from config import ADMIN_IDS
from keyboards.main import get_main_keyboard, get_back_to_main_keyboard
from data.models import db
from data.products_data import SHOP_INFO
from states.deposit import CaptchaStates
from utils.captcha import generate_captcha
from utils.reviews import get_reviews_text, TOTAL_PAGES


def get_reviews_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    buttons = []
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"reviews_page:{page-1}"))
    if page < TOTAL_PAGES:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"reviews_page:{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

router = Router()

WELCOME_IMAGE = "images/store.jpg"

WELCOME_TEXT = """Добро пожаловать в наш уютный магазин!
В нашем боте вы можете что-то купить!

Кол-во сделок: <b>70949 шт.</b>

<b>Твой баланс:</b> {balance} USD ({balance_ltc} LTC)
<b>Покупок:</b> {purchases}
<b>Персональная скидка:</b> {discount} %

Приглашены: {referrals}
Бонусов получено: {bonus} USD


При совершении покупки клиентом, которого вы пригласили - бонус будет автоматически зачислен на Ваш баланс. Вы получите уведомление о зачислении."""


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    user = db.get_user(message.from_user.id)
    if user:
        await show_main_menu(message)
        return
    
    captcha_text, captcha_image = generate_captcha()
    
    await state.update_data(captcha_answer=captcha_text)
    await state.set_state(CaptchaStates.waiting_for_captcha)
    
    photo = BufferedInputFile(captcha_image.read(), filename="captcha.png")
    
    captcha_msg = """
🔐 <b>ПРОВЕРКА БЕЗОПАСНОСТИ</b>

━━━━━━━━━━━━━━━━━━━━
Введите символы с картинки:
━━━━━━━━━━━━━━━━━━━━

⚠️ <i>Регистр не важен</i>
"""
    
    await message.answer_photo(
        photo=photo,
        caption=captcha_msg,
        parse_mode="HTML"
    )


@router.message(CaptchaStates.waiting_for_captcha)
async def check_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    correct_answer = data.get("captcha_answer", "")
    
    if message.text.upper().strip() == correct_answer.upper():
        await state.clear()
        
        db.create_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        await message.answer("✅ Проверка пройдена!")
        await show_main_menu(message)
    else:
        captcha_text, captcha_image = generate_captcha()
        await state.update_data(captcha_answer=captcha_text)
        
        photo = BufferedInputFile(captcha_image.read(), filename="captcha.png")
        
        await message.answer_photo(
            photo=photo,
            caption="❌ <b>Неверно!</b>\n\nПопробуйте еще раз.\nВведите символы с картинки:",
            parse_mode="HTML"
        )


async def show_main_menu(message: Message):
    user = db.get_user(message.from_user.id)
    balance = user.balance if user else 0
    purchases = user.total_orders if user else 0
    discount = 0
    referrals = 0
    bonus = 0
    balance_ltc = round(balance * 0.013, 2)
    
    welcome_text = WELCOME_TEXT.format(
        balance=balance,
        balance_ltc=balance_ltc,
        purchases=purchases,
        discount=discount,
        referrals=referrals,
        bonus=bonus
    )
    
    if os.path.exists(WELCOME_IMAGE):
        try:
            photo = FSInputFile(WELCOME_IMAGE)
            await message.answer_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            return
        except Exception:
            pass
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    if os.path.exists(WELCOME_IMAGE):
        try:
            photo = FSInputFile(WELCOME_IMAGE)
            await callback.message.answer_photo(
                photo=photo,
                caption=WELCOME_TEXT,
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            return
        except Exception:
            pass
    
    await callback.message.answer(
        WELCOME_TEXT,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    
    if not user:
        user = db.create_user(
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
    
    username_display = f"@{user.username}" if user.username else "Нет"
    
    profile_text = f"""
👤 <b>ВАШ ПРОФИЛЬ</b>

━━━━━━━━━━━━━━━━━━━━
🆔 ID: <code>{user.user_id}</code>
👤 Имя: {user.full_name}
📛 Username: {username_display}
💰 Баланс: <b>{user.balance:,} сум</b>
📦 Всего заказов: {user.total_orders}
📅 Регистрация: {user.registered_at}
━━━━━━━━━━━━━━━━━━━━
"""
    
    try:
        await callback.message.edit_text(
            profile_text,
            reply_markup=get_back_to_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.delete()
        await callback.message.answer(
            profile_text,
            reply_markup=get_back_to_main_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "rules")
async def show_rules(callback: CallbackQuery):
    rules_text = """Правила рассмотрения и заполнения заявки для уточнений при ненаходе:

https://telegra.ph/Pravila-Magazina-08-10"""
    try:
        await callback.message.edit_caption(
            caption=rules_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        try:
            await callback.message.edit_text(
                rules_text,
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.delete()
            await callback.message.answer(
                rules_text,
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )


@router.callback_query(F.data == "reviews")
async def show_reviews(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            get_reviews_text(1),
            reply_markup=get_reviews_keyboard(1),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.delete()
        await callback.message.answer(
            get_reviews_text(1),
            reply_markup=get_reviews_keyboard(1),
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("reviews_page:"))
async def show_reviews_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        get_reviews_text(page),
        reply_markup=get_reviews_keyboard(page),
        parse_mode="HTML"
    )


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав администратора!")
        return
    
    stats = db.get_stats()
    
    admin_text = f"""
🔐 <b>ADMIN PANEL</b>

━━━━━━━━━━━━━━━━━━━━
📊 <b>Статистика:</b>
👥 Всего пользователей: {stats['total_users']}
📦 Всего заказов: {stats['total_orders']}
💰 Общий доход: {stats['total_revenue']:,} сум
━━━━━━━━━━━━━━━━━━━━

<b>Команды:</b>
/broadcast - Рассылка
/users - Список пользователей
/add_balance [user_id] [amount] - Пополнить баланс
"""
    
    await message.answer(admin_text, parse_mode="HTML")


@router.message(Command("add_balance"))
async def add_balance_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.answer(
            "❌ Неверный формат!\n"
            "Правильно: /add_balance [user_id] [amount]"
        )
        return
    
    try:
        user_id = int(args[1])
        amount = int(args[2])
    except ValueError:
        await message.answer("❌ Неверные значения!")
        return
    
    if db.update_balance(user_id, amount):
        user = db.get_user(user_id)
        await message.answer(
            f"✅ Баланс успешно обновлен!\n"
            f"👤 Пользователь: {user.full_name}\n"
            f"💰 Новый баланс: {user.balance:,} сум"
        )
        
        try:
            await message.bot.send_message(
                user_id,
                f"💰 <b>Баланс пополнен!</b>\n\n"
                f"➕ Сумма: {amount:,} сум\n"
                f"💵 Новый баланс: {user.balance:,} сум",
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        await message.answer("❌ Пользователь не найден!")


@router.message(Command("confirm_crypto"))
async def confirm_crypto_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.answer(
            "❌ Неверный формат!\n"
            "Правильно: /confirm_crypto [user_id] [amount]"
        )
        return
    
    try:
        user_id = int(args[1])
        amount = int(args[2])
    except ValueError:
        await message.answer("❌ Неверные значения!")
        return
    
    if db.update_balance(user_id, amount):
        user = db.get_user(user_id)
        await message.answer(
            f"✅ Крипто-платеж подтвержден!\n"
            f"👤 Пользователь: {user.full_name}\n"
            f"💰 Новый баланс: {user.balance:,} сум"
        )
        
        try:
            await message.bot.send_message(
                user_id,
                f"💰 <b>Крипто-платеж подтвержден!</b>\n\n"
                f"➕ Сумма: {amount:,} сум\n"
                f"💵 Новый баланс: {user.balance:,} сум\n\n"
                f"Спасибо за оплату! 🙏",
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        await message.answer("❌ Пользователь не найден!")
