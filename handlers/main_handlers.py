from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import os

from config import ADMIN_IDS
from keyboards.main import get_main_keyboard, get_back_to_main_keyboard, get_reply_keyboard, get_menu_commands_keyboard, get_commands_list_keyboard
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

Кол-во сделок: <b>71012 шт.</b>

<b>Твой баланс:</b> {balance} USD ({balance_ltc} LTC)
<b>Покупок:</b> {purchases}
<b>Персональная скидка:</b> {discount} %

Приглашены: {referrals}
Бонусов получено: {bonus} USD

Пригласить друга и получить бонус: {referral_link}

При совершении покупки клиентом, которого вы пригласили - бонус будет автоматически зачислен на Ваш баланс. Вы получите уведомление о зачислении."""


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    # Referral parametrni tekshirish
    referral_id = None
    if message.text and len(message.text.split()) > 1:
        try:
            referral_id = int(message.text.split()[1])
        except (ValueError, IndexError):
            pass
    
    user = db.get_user(message.from_user.id)
    if user:
        await show_main_menu(message)
        return
    
    # Referral ID ni state'ga saqlash
    if referral_id:
        await state.update_data(referral_id=referral_id)
    
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
    referral_id = data.get("referral_id")
    
    if message.text.upper().strip() == correct_answer.upper():
        await state.clear()
        
        # Referral ID bilan foydalanuvchi yaratish
        db.create_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referral_id=referral_id
        )
        
        # Agar referral bo'lsa, xabar yuborish
        if referral_id:
            referrer = db.get_user(referral_id)
            if referrer:
                await message.answer(
                    f"✅ Проверка пройдена!\n\n"
                    f"🎉 Вы зарегистрированы по реферальной ссылке!\n"
                    f"Ваш реферер получил 1$ бонус.",
                    parse_mode="HTML"
                )
            else:
                await message.answer("✅ Проверка пройдена!")
        else:
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
    from config import BOT_USERNAME
    user = db.get_user(message.from_user.id)
    balance = user.balance if user else 0
    purchases = user.total_orders if user else 0
    discount = 0
    referrals = user.referrals_count if user else 0
    bonus = user.bonus_received if user else 0
    balance_ltc = round(balance * 0.013, 2)
    
    # Referral link yaratish
    referral_link = f"https://t.me/{BOT_USERNAME}?start={message.from_user.id}"
    
    welcome_text = WELCOME_TEXT.format(
        balance=balance,
        balance_ltc=balance_ltc,
        purchases=purchases,
        discount=discount,
        referrals=referrals,
        bonus=bonus,
        referral_link=referral_link
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
    await callback.answer()
    
    from config import BOT_USERNAME
    user = db.get_user(callback.from_user.id)
    balance = user.balance if user else 0
    purchases = user.total_orders if user else 0
    discount = 0
    referrals = user.referrals_count if user else 0
    bonus = user.bonus_received if user else 0
    balance_ltc = round(balance * 0.013, 2)
    
    # Referral link yaratish
    referral_link = f"https://t.me/{BOT_USERNAME}?start={callback.from_user.id}"
    
    welcome_text = WELCOME_TEXT.format(
        balance=balance,
        balance_ltc=balance_ltc,
        purchases=purchases,
        discount=discount,
        referrals=referrals,
        bonus=bonus,
        referral_link=referral_link
    )
    
    try:
        await callback.message.edit_text(
            welcome_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        if os.path.exists(WELCOME_IMAGE):
            try:
                photo = FSInputFile(WELCOME_IMAGE)
                await callback.message.answer_photo(
                    photo=photo,
                    caption=welcome_text,
                    reply_markup=get_main_keyboard(),
                    parse_mode="HTML"
                )
                return
            except Exception:
                pass
        
        await callback.message.answer(
            welcome_text,
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


@router.callback_query(F.data == "last_orders")
async def show_last_orders(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден!", show_alert=True)
        return
    
    orders = db.get_user_orders(callback.from_user.id)
    
    if not orders:
        text = "📋 <b>ПОСЛЕДНИЕ ЗАКАЗЫ</b>\n\nУ вас пока нет заказов."
    else:
        text = "📋 <b>ПОСЛЕДНИЕ ЗАКАЗЫ</b>\n\n"
        # Oxirgi 5 ta buyurtmani ko'rsatish
        for order in orders[-5:][::-1]:
            text += f"🆔 #{order.order_id}\n"
            text += f"📦 {order.product_name}\n"
            text += f"💰 {order.price:,} сум\n"
            text += f"📅 {order.created_at}\n"
            text += f"✅ {order.status}\n"
            text += "━━━━━━━━━━━━━━━━━━━━\n"
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.delete()
        await callback.message.answer(
            text,
            reply_markup=get_back_to_main_keyboard(),
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


# Inline keyboard buyruqlari uchun handlerlar
@router.callback_query(F.data == "cmd_start")
async def cmd_start_inline(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await show_main_menu(callback.message)


@router.callback_query(F.data == "cmd_list")
async def cmd_list_inline(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    from handlers.vitrina_handlers import show_vitrina_handler
    await show_vitrina_handler(callback.message)


@router.callback_query(F.data == "cmd_support")
async def cmd_support_inline(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    support_text = """
🧾 <b>ПОДДЕРЖКА</b>

━━━━━━━━━━━━━━━━━━━━
Есть вопросы? Мы поможем!

🕐 Время работы: 09:00 - 21:00
📱 Время ответа: 5-30 минут
━━━━━━━━━━━━━━━━━━━━

Выберите действие:
"""
    from keyboards.support import get_support_keyboard
    await callback.message.answer(
        support_text,
        reply_markup=get_support_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "cmd_rules")
async def cmd_rules_inline(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    rules_text = """Правила рассмотрения и заполнения заявки для уточнений при ненаходе:

https://telegra.ph/Pravila-Magazina-08-10"""
    await callback.message.answer(
        rules_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "cmd_info")
async def cmd_info_inline(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    from config import SHOP_NAME, SHOP_DESCRIPTION, CHANNEL_USERNAME
    info_text = f"""
ℹ️ <b>{SHOP_NAME} haqida</b>

{SHOP_DESCRIPTION}

━━━━━━━━━━━━━━━━━━━━
🏪 Biz 2020-yildan buyon faoliyat yuritamiz
🌍 O'zbekiston bo'ylab yetkazib berish
📦 1000+ mamnun mijozlar
━━━━━━━━━━━━━━━━━━━━

Quyidagi bo'limlardan birini tanlang:
"""
    from keyboards.info import get_info_keyboard
    await callback.message.answer(
        info_text,
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "connect_bot")
async def connect_bot_handler(callback: CallbackQuery):
    await callback.answer("⏳ Временно не работает", show_alert=True)


# Har qanday matn yozilganda glavniy ekranga qaytarish
# Faqat state bo'sh bo'lganda ishlaydi (boshqa handlerlar state'larni ishlatayotganda ishlamaydi)
# Bu handler eng oxirida ishlashi kerak, shuning uchun priority past
@router.message(F.text & ~F.text.startswith("/"))
async def handle_any_text(message: Message, state: FSMContext):
    # Agar state bo'sh bo'lsa, glavniy ekranga qaytarish
    # Lekin boshqa router'larda state bo'lsa, ularni ishlatishga ruxsat berish
    current_state = await state.get_state()
    if current_state is None:
        await show_main_menu(message)
    # Agar state bor bo'lsa, boshqa handlerlarga ruxsat berish (return qilmaymiz)


# Buyruqlar
@router.message(Command("list"))
async def cmd_list(message: Message, state: FSMContext):
    await state.clear()
    from handlers.vitrina_handlers import show_vitrina_handler
    await show_vitrina_handler(message)


@router.message(Command("support"))
async def cmd_support(message: Message, state: FSMContext):
    await state.clear()
    from handlers.support_handlers import show_support
    # CallbackQuery emas Message, shuning uchun alohida handler yozish kerak
    support_text = """
🧾 <b>ПОДДЕРЖКА</b>

━━━━━━━━━━━━━━━━━━━━
Есть вопросы? Мы поможем!

🕐 Время работы: 09:00 - 21:00
📱 Время ответа: 5-30 минут
━━━━━━━━━━━━━━━━━━━━

Выберите действие:
"""
    from keyboards.support import get_support_keyboard
    await message.answer(
        support_text,
        reply_markup=get_support_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("rules"))
async def cmd_rules(message: Message, state: FSMContext):
    await state.clear()
    rules_text = """Правила рассмотрения и заполнения заявки для уточнений при ненаходе:

https://telegra.ph/Pravila-Magazina-08-10"""
    await message.answer(
        rules_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("info"))
async def cmd_info(message: Message, state: FSMContext):
    await state.clear()
    from config import SHOP_NAME, SHOP_DESCRIPTION, CHANNEL_USERNAME
    info_text = f"""
ℹ️ <b>{SHOP_NAME} haqida</b>

{SHOP_DESCRIPTION}

━━━━━━━━━━━━━━━━━━━━
🏪 Biz 2020-yildan buyon faoliyat yuritamiz
🌍 O'zbekiston bo'ylab yetkazib berish
📦 1000+ mamnun mijozlar
━━━━━━━━━━━━━━━━━━━━

Quyidagi bo'limlardan birini tanlang:
"""
    from keyboards.info import get_info_keyboard
    await message.answer(
        info_text,
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
