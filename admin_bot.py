import asyncio
import logging
import sys
import json
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

from config import ADMIN_BOT_TOKEN, BOT_TOKEN, ADMIN_IDS
from data.models import db

# Vitrina handlerlaridan ma'lumotlar
try:
    from handlers.vitrina_handlers import PRODUCTS, DISTRICTS, PICKUP_INFO
except ImportError:
    # Agar import qilishda muammo bo'lsa, bo'sh dict'lar
    PRODUCTS = {}
    DISTRICTS = {}
    PICKUP_INFO = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

bot = Bot(token=ADMIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

pending_applications = {}


class AdminStates(StatesGroup):
    waiting_for_review_rating = State()  # Yulduzcha tanlash
    waiting_for_review_text = State()  # Otziv matni
    waiting_for_broadcast = State()


def get_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Заявки", callback_data="show_applications")
            ],
            [
                InlineKeyboardButton(text="👥 Пользователи", callback_data="show_users")
            ],
            [
                InlineKeyboardButton(text="📝 Добавить отзыв", callback_data="add_review")
            ],
            [
                InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast")
            ]
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"Admin bot /start command from user ID: {message.from_user.id}")
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


# Otziv qo'shish
@dp.callback_query(F.data == "add_review")
async def add_review_start(callback: CallbackQuery, state: FSMContext):
    logger.info(f"add_review callback from user ID: {callback.from_user.id}")
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    await callback.answer()
    
    # Yulduzcha tanlash uchun keyboard
    rating_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ 1", callback_data="rating_1"),
                InlineKeyboardButton(text="⭐⭐ 2", callback_data="rating_2"),
                InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data="rating_3")
            ],
            [
                InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data="rating_4"),
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data="rating_5")
            ],
            [
                InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_review")
            ]
        ]
    )
    
    try:
        await callback.message.edit_text(
            "📝 <b>ДОБАВИТЬ ОТЗЫВ</b>\n\n"
            "Сначала выберите рейтинг (количество звезд):",
            reply_markup=rating_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        await callback.message.answer(
            "📝 <b>ДОБАВИТЬ ОТЗЫВ</b>\n\n"
            "Сначала выберите рейтинг (количество звезд):",
            reply_markup=rating_keyboard,
            parse_mode="HTML"
        )
    await state.set_state(AdminStates.waiting_for_review_rating)


@dp.callback_query(F.data.startswith("rating_"))
async def select_rating(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    
    await callback.answer(f"Выбрано: {rating} звезд")
    await callback.message.edit_text(
        f"📝 <b>ДОБАВИТЬ ОТЗЫВ</b>\n\n"
        f"⭐ Рейтинг: {rating} звезд\n\n"
        f"Теперь введите текст отзыва:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_review_text)


@dp.callback_query(F.data == "cancel_review")
async def cancel_review(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Отменено")
    await callback.message.edit_text(
        "🔐 <b>ADMIN PANEL</b>\n\n"
        "Добро пожаловать в панель администратора!\n"
        "Выберите действие:",
        reply_markup=get_admin_menu(),
        parse_mode="HTML"
    )


@dp.message(AdminStates.waiting_for_review_text)
async def add_review_receive(message: Message, state: FSMContext):
    logger.info(f"add_review_receive called from user ID: {message.from_user.id}")
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(f"Unauthorized user tried to add review: {message.from_user.id}")
        return
    
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст отзыва!")
        return
    
    data = await state.get_data()
    rating = data.get("rating", 5)
    review_text = message.text
    
    logger.info(f"Adding review: rating={rating}, text={review_text[:50]}...")
    
    # Reviews faylini yangilash
    try:
        import json
        import os
        from datetime import datetime
        
        reviews_file = "data/reviews.json"
        
        # Agar fayl bo'lmasa, yaratish
        if not os.path.exists(reviews_file):
            os.makedirs(os.path.dirname(reviews_file), exist_ok=True)
            reviews_data = []
        else:
            try:
                with open(reviews_file, "r", encoding="utf-8") as f:
                    reviews_data = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in reviews file, creating new one")
                reviews_data = []
        
        # Yangi otziv qo'shish
        new_review = {
            "text": review_text,
            "rating": rating,
            "date": datetime.now().strftime("%d.%m.%Y"),
            "time": datetime.now().strftime("%H:%M")
        }
        reviews_data.append(new_review)
        
        # Faylga saqlash
        with open(reviews_file, "w", encoding="utf-8") as f:
            json.dump(reviews_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Review saved to file: {reviews_file}")
        
        stars = "⭐" * rating
        await message.answer(
            f"✅ <b>Отзыв добавлен!</b>\n\n"
            f"{stars}\n"
            f"📝 Текст: {review_text}\n\n"
            f"Отзыв успешно добавлен в список отзывов.",
            reply_markup=get_admin_menu(),
            parse_mode="HTML"
        )
        logger.info(f"Review added successfully: rating={rating}, text={review_text[:50]}...")
    except Exception as e:
        logger.error(f"Error adding review: {e}", exc_info=True)
        await message.answer(
            f"❌ Ошибка при добавлении отзыва: {e}\n\n"
            f"Попробуйте еще раз или обратитесь к разработчику.",
            reply_markup=get_admin_menu()
        )
    
    await state.clear()


# Reklama/elon qilish
@dp.callback_query(F.data == "broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    logger.info(f"broadcast callback from user ID: {callback.from_user.id}")
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    await callback.answer()
    try:
        await callback.message.edit_text(
            "📢 <b>РАССЫЛКА</b>\n\n"
            "Введите текст сообщения, которое будет отправлено всем пользователям:\n\n"
            "Вы можете отправить текст, фото или документ.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        await callback.message.answer(
            "📢 <b>РАССЫЛКА</b>\n\n"
            "Введите текст сообщения, которое будет отправлено всем пользователям:\n\n"
            "Вы можете отправить текст, фото или документ.",
            parse_mode="HTML"
        )
    await state.set_state(AdminStates.waiting_for_broadcast)


@dp.message(AdminStates.waiting_for_broadcast)
async def broadcast_receive(message: Message, state: FSMContext):
    logger.info(f"broadcast_receive called from user ID: {message.from_user.id}")
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(f"Unauthorized user tried to broadcast: {message.from_user.id}")
        return
    
    # Text yoki caption olish (photo yoki document bo'lsa)
    if message.text:
        broadcast_text = message.text
    elif message.caption:
        broadcast_text = message.caption
    else:
        await message.answer("❌ Текст сообщения не найден!", reply_markup=get_admin_menu())
        await state.clear()
        return
    
    # Barcha foydalanuvchilarga yuborish
    users = db.get_all_users()
    total_users = len(users)
    logger.info(f"Starting broadcast to {total_users} users")
    logger.info(f"Using BOT_TOKEN: {BOT_TOKEN[:10]}... (first 10 chars)")
    
    if total_users == 0:
        await message.answer(
            "❌ <b>Нет пользователей для рассылки!</b>",
            reply_markup=get_admin_menu(),
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    success_count = 0
    fail_count = 0
    
    await message.answer(
        f"📢 <b>Рассылка начата...</b>\n\n"
        f"Всего пользователей: {total_users}\n"
        f"Отправка сообщений...",
        parse_mode="HTML"
    )
    
    # Test uchun birinchi foydalanuvchiga yuborish
    if users:
        test_user = users[0]
        logger.info(f"Test: Sending to first user {test_user.user_id} ({test_user.full_name})")
    
    # Agar photo yoki document bo'lsa, uni yuklab olish
    photo_file_path = None
    document_file_path = None
    
    if message.photo:
        # Photo'ni yuklab olish
        photo_file_id = message.photo[-1].file_id
        try:
            async with aiohttp.ClientSession() as temp_session:
                get_file_url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/getFile"
                file_response = await temp_session.post(get_file_url, json={"file_id": photo_file_id})
                file_data = await file_response.json()
                if file_data.get("ok"):
                    file_path = file_data["result"]["file_path"]
                    photo_file_path = f"https://api.telegram.org/file/bot{ADMIN_BOT_TOKEN}/{file_path}"
                    logger.info(f"Photo file path: {photo_file_path}")
        except Exception as e:
            logger.error(f"Error getting photo file: {e}")
    elif message.document:
        # Document'ni yuklab olish
        document_file_id = message.document.file_id
        try:
            async with aiohttp.ClientSession() as temp_session:
                get_file_url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/getFile"
                file_response = await temp_session.post(get_file_url, json={"file_id": document_file_id})
                file_data = await file_response.json()
                if file_data.get("ok"):
                    file_path = file_data["result"]["file_path"]
                    document_file_path = f"https://api.telegram.org/file/bot{ADMIN_BOT_TOKEN}/{file_path}"
                    logger.info(f"Document file path: {document_file_path}")
        except Exception as e:
            logger.error(f"Error getting document file: {e}")
    
    async with aiohttp.ClientSession() as session:
        for user in users:
            try:
                logger.info(f"Attempting to send message to user {user.user_id} ({user.full_name})")
                # Agar photo yoki document bo'lsa
                if photo_file_path:
                    # Photo yuborish - URL orqali
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                    payload = {
                        "chat_id": user.user_id,
                        "photo": photo_file_path,
                        "caption": broadcast_text,
                        "parse_mode": "HTML"
                    }
                    response = await session.post(url, json=payload)
                elif document_file_path:
                    # Document yuborish - URL orqali
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                    payload = {
                        "chat_id": user.user_id,
                        "document": document_file_path,
                        "caption": broadcast_text,
                        "parse_mode": "HTML"
                    }
                    response = await session.post(url, json=payload)
                else:
                    # Oddiy text yuborish
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": user.user_id,
                        "text": broadcast_text,
                        "parse_mode": "HTML"
                    }
                    response = await session.post(url, json=payload)
                
                # Response'ni o'qish
                try:
                    response_data = await response.json()
                except Exception as e:
                    response_text = await response.text()
                    response_data = {"ok": False, "description": f"Invalid JSON: {response_text[:100]}"}
                    logger.error(f"JSON parse error for user {user.user_id}: {e}, response: {response_text[:200]}")
                
                logger.info(f"Response for user {user.user_id}: status={response.status}, ok={response_data.get('ok')}, description={response_data.get('description', 'N/A')}")
                
                if response.status == 200 and response_data.get("ok"):
                    success_count += 1
                    if success_count % 10 == 0:
                        logger.info(f"Sent to {success_count}/{total_users} users")
                else:
                    fail_count += 1
                    error_text = response_data.get("description", "Unknown error")
                    error_code = response_data.get("error_code", "N/A")
                    logger.error(f"❌ Failed to send to user {user.user_id} ({user.full_name}): Error {error_code}: {error_text}")
                    # Admin'ga xatolik haqida xabar yuborish
                    if fail_count == 1:  # Faqat birinchi xatolikni ko'rsatish
                        try:
                            await message.answer(
                                f"⚠️ <b>Xatolik topildi:</b>\n\n"
                                f"Foydalanuvchi: {user.full_name} (ID: {user.user_id})\n"
                                f"Xatolik: {error_text}\n\n"
                                f"Barcha xatoliklar log'da ko'rsatiladi.",
                                parse_mode="HTML"
                            )
                        except:
                            pass
            except Exception as e:
                logger.error(f"Exception sending to user {user.user_id}: {type(e).__name__}: {e}")
                fail_count += 1
    
    await message.answer(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📊 Статистика:\n"
        f"✅ Отправлено: {success_count}\n"
        f"❌ Ошибок: {fail_count}\n"
        f"📝 Всего: {total_users}",
        reply_markup=get_admin_menu(),
        parse_mode="HTML"
    )
    
    logger.info(f"Broadcast completed: {success_count} success, {fail_count} failed")
    await state.clear()


# Vitrina handlerlari uchun
@dp.callback_query(F.data.startswith("vcrypto_approve:"))
async def vcrypto_approve(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    user_id = int(parts[1])
    item_key = parts[2]
    district_key = parts[3]
    application_id = parts[4]
    
    product = PRODUCTS.get(item_key, {})
    district_name = DISTRICTS.get(district_key, "")
    
    weight = product.get("weight", "0.5g")
    pickup_data = PICKUP_INFO.get(district_key, {}).get(weight)
    
    if pickup_data:
        pickup_text = pickup_data["text"]
        images = pickup_data["images"]
    else:
        pickup_text = f"📦 ТОВАР: {product.get('name', '')}\n📍 РАЙОН: {district_name}"
        images = []
    
    await callback.message.edit_text(
        f"✅ <b>ЗАЯВКА #{application_id} ПОДТВЕРЖДЕНА</b>",
        parse_mode="HTML"
    )
    
    try:
        order_header = f"<b>#{application_id}</b>\n<b>{product.get('name', '')} (Ташкент, {district_name})</b>\n\n"
        full_text = order_header + pickup_text
        
        if images:
            for img_url in images:
                full_text += f"\n{img_url}"
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": full_text,
                "parse_mode": "HTML"
            }
            await session.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")


@dp.callback_query(F.data.startswith("vcrypto_reject:"))
async def vcrypto_reject(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    user_id = int(parts[1])
    application_id = parts[2]
    
    await callback.message.edit_text(
        f"❌ <b>ЗАЯВКА #{application_id} ОТКЛОНЕНА</b>",
        parse_mode="HTML"
    )
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": f"❌ <b>Заявка #{application_id} отклонена</b>\n\nОбратитесь в поддержку.",
                "parse_mode": "HTML"
            }
            await session.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")


@dp.callback_query(F.data.startswith("vconfirm_dep:"))
async def vconfirm_dep(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    user_id = int(parts[1])
    amount = int(parts[2])
    application_id = parts[3]
    
    db.update_balance(user_id, amount)
    user = db.get_user(user_id)
    
    await callback.message.edit_text(
        f"✅ <b>ЗАЯВКА #{application_id} ПОДТВЕРЖДЕНА</b>\n\n💵 Зачислено: {amount} $",
        parse_mode="HTML"
    )
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": (
                    f"✅ <b>БАЛАНС ПОПОЛНЕН!</b>\n\n"
                    f"💰 Зачислено: {amount} $\n"
                    f"💵 Баланс: {user.balance} $"
                ),
                "parse_mode": "HTML"
            }
            await session.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")


@dp.callback_query(F.data.startswith("vreject_dep:"))
async def vreject_dep(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    user_id = int(parts[1])
    application_id = parts[2]
    
    await callback.message.edit_text(
        f"❌ <b>ЗАЯВКА #{application_id} ОТКЛОНЕНА</b>",
        parse_mode="HTML"
    )
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": f"❌ <b>Заявка #{application_id} отклонена</b>",
                "parse_mode": "HTML"
            }
            await session.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")


async def main():
    logger.info("Admin Bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Admin Bot to'xtatildi")
