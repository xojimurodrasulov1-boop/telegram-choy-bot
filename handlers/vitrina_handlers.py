import random
import logging
import os
import aiohttp
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, LTC_ADDRESS, BTC_ADDRESS, ADMIN_BOT_TOKEN
from data.models import db

router = Router()
logger = logging.getLogger(__name__)


def format_crypto_amount(amount: float, crypto_type: str) -> str:
    """Kripto valyuta miqdorini aniq formatlash"""
    if crypto_type == "ltc":
        # LTC uchun 4 xona
        return f"{amount:.4f}".rstrip('0').rstrip('.')
    else:
        # BTC uchun 8 xona
        return f"{amount:.8f}".rstrip('0').rstrip('.')

PRODUCTS = {
    "euro_hash_05": {
        "name": "🍫 Euro Hash 0.5",
        "price_usd": 19,
        "price_rub": 7220,
        "old_price_usd": 21,
        "weight": "0.5g",
        "description": """💯Лучший в своем деле💯

Любишь когда тебя убивает?☠️

🍫 Euro Hash сможет это сделать с одной 
плюшки😏

Всего один вдох и ты растечешься по 
креслу, у тебя появится улыбка на лице, 
тебя окутает безмятежность а твои мысли
 унесутся в нирвану🫠

Хочешь проверить себя на стойкость? Тогда 
тебе точно стоит ощутить на себе 
🍫 Euro Hash"""
    },
    "euro_hash_1": {
        "name": "🍫 Euro Hash 1",
        "price_usd": 42,
        "price_rub": 15960,
        "old_price_usd": 48,
        "weight": "1g",
        "description": """💯Лучший в своем деле💯

Любишь когда тебя убивает?☠️

🍫 Euro Hash сможет это сделать с одной 
плюшки😏

Всего один вдох и ты растечешься по 
креслу, у тебя появится улыбка на лице, 
тебя окутает безмятежность а твои мысли
 унесутся в нирвану🫠

Хочешь проверить себя на стойкость? Тогда 
тебе точно стоит ощутить на себе 
🍫 Euro Hash"""
    },
    "euro_hash_3": {
        "name": "🍫 Euro Hash 3",
        "price_usd": 90,
        "price_rub": 34200,
        "old_price_usd": 102,
        "weight": "3g",
        "description": """💯Лучший в своем деле💯

Любишь когда тебя убивает?☠️

🍫 Euro Hash сможет это сделать с одной 
плюшки😏

Всего один вдох и ты растечешься по 
креслу, у тебя появится улыбка на лице, 
тебя окутает безмятежность а твои мысли
 унесутся в нирвану🫠

Хочешь проверить себя на стойкость? Тогда 
тебе точно стоит ощутить на себе 
🍫 Euro Hash"""
    },
    "mef_snow_1": {
        "name": "Меф - ❄️SNOW❄️ - 1г",
        "price_usd": 19,
        "price_rub": 7270,
        "weight": "1г",
        "description": """Меф - ❄️SNOW❄️

Высокое качество, проверенное временем."""
    },
    "mef_snow_15": {
        "name": "Меф - ❄️SNOW❄️ - 1.5г",
        "price_usd": 25,
        "price_rub": 9560,
        "weight": "1.5г",
        "description": """Меф - ❄️SNOW❄️

Высокое качество, проверенное временем."""
    },
    "mef_snow_2": {
        "name": "Меф - ❄️SNOW❄️ - 2г",
        "price_usd": 32,
        "price_rub": 12230,
        "weight": "2г",
        "description": """Меф - ❄️SNOW❄️

Высокое качество, проверенное временем."""
    },
    "mef_snow_3": {
        "name": "Меф - ❄️SNOW❄️ - 3г",
        "price_usd": 50,
        "price_rub": 19190,
        "weight": "3г",
        "description": """Меф - ❄️SNOW❄️

Высокое качество, проверенное временем."""
    },
    "lsd_1": {
        "name": "😈 LSD 😈 - 1шт",
        "price_usd": 10,
        "price_rub": 3790,
        "weight": "1шт",
        "description": """😈 LSD 😈

Качественный продукт."""
    }
}

DISTRICTS = {
    "chilonzor": "Чилонзор",
    "sergeli": "Сергели"
}

PICKUP_INFO = {
    "sergeli": {
        "0.5g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍫Euro Hash
⚖️ ФАСОВКА: 0.5g
🔎 ТИП КЛАДА: ТАЙНИК
📍 РАЙОН: СЕРГЕЛИ
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ТАЙНИК ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s.fiho-st.sbs/i/2025/12/73e18/ba7e5368285be88a3a52d1273854a6af-img_7183.jpg",
                "https://s.fiho-st.sbs/i/2025/12/73e18/2b16fbddd8c30438ff7b66c90683e9d3-img_7182.jpg"
            ]
        },
        "1g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍫Euro Hash
⚖️ ФАСОВКА: 1g
🔎 ТИП КЛАДА: ТАЙНИК
📍 РАЙОН: СЕРГЕЛИ
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ТАЙНИК ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s.fiho-st.sbs/i/2025/12/73e18/ba7e5368285be88a3a52d1273854a6af-img_7183.jpg",
                "https://s.fiho-st.sbs/i/2025/12/73e18/2b16fbddd8c30438ff7b66c90683e9d3-img_7182.jpg"
            ]
        },
        "3g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍫Euro Hash
⚖️ ФАСОВКА: 3g
🔎 ТИП КЛАДА: ТАЙНИК
📍 РАЙОН: СЕРГЕЛИ
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ТАЙНИК ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s.fiho-st.sbs/i/2025/12/73e18/ba7e5368285be88a3a52d1273854a6af-img_7183.jpg",
                "https://s.fiho-st.sbs/i/2025/12/73e18/2b16fbddd8c30438ff7b66c90683e9d3-img_7182.jpg"
            ]
        },
        "0.3g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍋HOTE Tropics Lemon HAZA
⚖️ ФАСОВКА: 0.3g
🔎 ТИП КЛАДА: ТАЙНИК
📍 РАЙОН: СЕРГЕЛИ
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ТАЙНИК ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s1.fiho-st.sbs/i/2025/11/33923/1f884651c9d2ea15a8068960ba753eb9-img_6450.jpg",
                "https://s.fiho-st.sbs/i/2025/11/33923/2cb2986bdc0fbb67caecd5c4ccbd3cda-img_6449.jpg"
            ]
        }
    },
    "chilonzor": {
        "0.5g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍫Euro Hash
⚖️ ФАСОВКА: 0.5g
🔎 ТИП КЛАДА: ПРИКОП
📍 РАЙОН: ЧИЛОНЗОР
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ПРИКОП 2-3см ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s.fiho-st.sbs/i/2025/11/33923/7f2143f6155ac2ae7adc0e5bedc93e5a-img_6444.jpg",
                "https://s1.fiho-st.sbs/i/2025/11/33923/36d492b119dd24f39bb45f73362bb4fd-img_6443.jpg"
            ]
        },
        "1g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍫Euro Hash
⚖️ ФАСОВКА: 1g
🔎 ТИП КЛАДА: ПРИКОП
📍 РАЙОН: ЧИЛОНЗОР
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ПРИКОП 2-3см ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s.fiho-st.sbs/i/2025/11/33923/7f2143f6155ac2ae7adc0e5bedc93e5a-img_6444.jpg",
                "https://s1.fiho-st.sbs/i/2025/11/33923/36d492b119dd24f39bb45f73362bb4fd-img_6443.jpg"
            ]
        },
        "3g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍫Euro Hash
⚖️ ФАСОВКА: 3g
🔎 ТИП КЛАДА: ПРИКОП
📍 РАЙОН: ЧИЛОНЗОР
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ПРИКОП 2-3см ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s.fiho-st.sbs/i/2025/11/33923/7f2143f6155ac2ae7adc0e5bedc93e5a-img_6444.jpg",
                "https://s1.fiho-st.sbs/i/2025/11/33923/36d492b119dd24f39bb45f73362bb4fd-img_6443.jpg"
            ]
        },
        "0.3g": {
            "text": """«КАЙФ - И ТОЧКА»™️
📦 ТОВАР: 🍋HOTE Tropics Lemon HAZA
⚖️ ФАСОВКА: 0.3g
🔎 ТИП КЛАДА: ПРИКОП
📍 РАЙОН: ЧИЛОНЗОР
🎨 ЦВЕТ ИЗО: ЧЕРНАЯ

Клад расположен в указанном месте, ПРИКОП 2-3см ровно по стрелкам на фотографии📸

Поиски проводите аккуратно, предварительно изучив место клада и прицелившись, НЕ СМАХНИТЕ КЛАД РУКОЙ, будьте аккуратны‼️

С КАЙФОМ ВАС ЖДУТ легкие НАХОДЫ и ОТЛИЧНОЕ НАСТРОЕНИЕ! Витрина пополняется каждый день! ВСЕ БУДЕТ КАЙФ - И ТОЧКА.💯""",
            "images": [
                "https://s.fiho-st.sbs/i/2025/11/33923/7f2143f6155ac2ae7adc0e5bedc93e5a-img_6444.jpg",
                "https://s1.fiho-st.sbs/i/2025/11/33923/36d492b119dd24f39bb45f73362bb4fd-img_6443.jpg"
            ]
        }
    }
}

LTC_RATE = 0.013
BTC_RATE = 0.0000098


def get_vitrina_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, product in PRODUCTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=product["name"],
                callback_data=f"vitem:{key}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_districts_keyboard(item_key: str) -> InlineKeyboardMarkup:
    buttons = []
    for key, name in DISTRICTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"vdist:{item_key}:{key}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="vitrina")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_vitrina_handler(obj):
    """Vitrina ko'rsatish - CallbackQuery yoki Message qabul qiladi"""
    if isinstance(obj, CallbackQuery):
        try:
            await obj.message.delete()
        except Exception:
            pass
        await obj.message.answer(
            "🏪 <b>ВИТРИНА</b>\n\nВыберите товар:",
            reply_markup=get_vitrina_keyboard(),
            parse_mode="HTML"
        )
    elif isinstance(obj, Message):
        await obj.answer(
            "🏪 <b>ВИТРИНА</b>\n\nВыберите товар:",
            reply_markup=get_vitrina_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "vitrina")
async def show_vitrina(callback: CallbackQuery):
    logger.info("=== VITRINA BOSILDI! ===")
    await show_vitrina_handler(callback)


@router.callback_query(F.data.startswith("vitem:"))
async def show_item(callback: CallbackQuery, state: FSMContext):
    item_key = callback.data.replace("vitem:", "")
    
    product = PRODUCTS.get(item_key)
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    await state.update_data(item_key=item_key)
    
    try:
        await callback.message.edit_text(
            f"<b>Отличный выбор!</b>\nА теперь выбери район:",
            reply_markup=get_districts_keyboard(item_key),
            parse_mode="HTML"
        )
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            f"<b>Отличный выбор!</b>\nА теперь выбери район:",
            reply_markup=get_districts_keyboard(item_key),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("vdist:"))
async def select_district(callback: CallbackQuery, state: FSMContext):
    logger.info(f"=== SELECT_DISTRICT BOSILDI! Data: {callback.data} ===")
    parts = callback.data.split(":")
    if len(parts) < 3:
        logger.error(f"vdist: Not enough parts: {parts}")
        return
    
    item_key = parts[1]
    district_key = parts[2]
    
    product = PRODUCTS.get(item_key)
    district_name = DISTRICTS.get(district_key, "")
    
    logger.info(f"Item key: {item_key}, District key: {district_key}, Product: {product}, District name: {district_name}")
    
    if not product or not district_name:
        logger.error(f"Product or district not found: product={product}, district={district_name}")
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    await state.update_data(
        item_key=item_key,
        district_key=district_key,
        district_name=district_name,
        item_name=product['name'],
        price=product['price_usd']
    )
    
    # Тип tanlash uchun keyboard
    type_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Прикоп", callback_data=f"vtype:{item_key}:{district_key}:prikop")],
            [InlineKeyboardButton(text="Магнит", callback_data=f"vtype:{item_key}:{district_key}:magnet")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"vitem:{item_key}")]
        ]
    )
    
    logger.info(f"Type keyboard created: {type_keyboard}")
    
    try:
        await callback.message.edit_text(
            "<b>Выберите тип:</b>",
            reply_markup=type_keyboard,
            parse_mode="HTML"
        )
        logger.info("Message edited successfully")
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            "<b>Выберите тип:</b>",
            reply_markup=type_keyboard,
            parse_mode="HTML"
        )
        logger.info("New message sent")
    await callback.answer()


@router.callback_query(F.data.startswith("vtype:"))
async def select_type(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    
    item_key = parts[1]
    district_key = parts[2]
    pickup_type = parts[3]  # prikop yoki magnet
    
    product = PRODUCTS.get(item_key)
    district_name = DISTRICTS.get(district_key, "")
    
    if not product or not district_name:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    await state.update_data(
        item_key=item_key,
        district_key=district_key,
        district_name=district_name,
        pickup_type=pickup_type,
        item_name=product['name'],
        price=product['price_usd']
    )
    
    user = db.get_user(callback.from_user.id)
    balance = user.balance if user else 0
    balance_ltc = round(balance * LTC_RATE, 2)
    
    old_price = product.get("old_price_usd")
    price_rub = product.get("price_rub")
    
    # Agar rubl narxi bo'lsa, uni ham ko'rsatish
    if price_rub:
        if old_price:
            price_text = f"<s>{old_price}$</s> {product['price_usd']}$ ({price_rub} руб.)"
        else:
            price_text = f"{product['price_usd']}$ ({price_rub} руб.)"
    else:
        if old_price:
            price_text = f"<s>{old_price}$</s> {product['price_usd']}$"
        else:
            price_text = f"{product['price_usd']}$"
    
    product_name_with_location = f"{product['name']} (Ташкент, {district_name})"
    
    price = product['price_usd']
    can_buy_with_balance = balance >= price
    
    buttons = []
    if can_buy_with_balance:
        buttons.append([InlineKeyboardButton(text="Оплатить с баланса", callback_data=f"vbuy_balance:{item_key}:{district_key}:{pickup_type}")])
        buttons.append([
            InlineKeyboardButton(text="LTC", callback_data=f"vbuy_crypto:ltc:{item_key}:{district_key}:{pickup_type}"),
            InlineKeyboardButton(text="BTC", callback_data=f"vbuy_crypto:btc:{item_key}:{district_key}:{pickup_type}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="LTC", callback_data=f"vbuy_crypto:ltc:{item_key}:{district_key}:{pickup_type}"),
            InlineKeyboardButton(text="BTC", callback_data=f"vbuy_crypto:btc:{item_key}:{district_key}:{pickup_type}")
        ])
        buttons.append([
            InlineKeyboardButton(text="🎁 Промокод", callback_data="promokod"),
            InlineKeyboardButton(text="💳 UzCard/Humo", callback_data="uzcard_humo")
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"vdist:{item_key}:{district_key}")])
    
    buy_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    text = f"""<b>{product_name_with_location}</b>

{product['description']}

<b>Цена:</b> {price_text}

⚠️ У вас нет персональной скидки!
Покупайте в магазине и получайте скидку для постоянных клиентов.
Чем больше покупок - тем выше ваша скидка!
    
💰 <b>Твой баланс:</b> {balance} $ ({balance_ltc} LTC)
"""
    
    # Agar Euro Hash yoki Меф SNOW mahsuloti bo'lsa, rasm qo'shish
    product_name = product.get('name', '')
    image_file = None
    
    if 'Euro Hash' in product_name or 'euro' in product_name.lower():
        image_file = "eurohash.jpg"
    elif 'Меф' in product_name or 'SNOW' in product_name or 'mef' in product_name.lower():
        image_file = "yangi tavarlar .jpg"
    
    if image_file and os.path.exists(image_file):
        try:
            photo = FSInputFile(image_file)
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=buy_keyboard,
                parse_mode="HTML"
            )
            return
        except Exception as e:
            logger.error(f"Error sending product image: {e}")
    
    try:
        await callback.message.edit_text(text, reply_markup=buy_keyboard, parse_mode="HTML")
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=buy_keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("vbuy_balance:"))
async def process_buy_balance(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    
    item_key = parts[1]
    district_key = parts[2]
    pickup_type = parts[3] if len(parts) > 3 else "prikop"  # prikop yoki magnet
    
    product = PRODUCTS.get(item_key)
    district_name = DISTRICTS.get(district_key, "")
    
    if not product:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    await state.update_data(pickup_type=pickup_type)
    
    user = db.get_user(callback.from_user.id)
    price = product['price_usd']
    
    if not user or user.balance < price:
        await callback.answer("❌ Недостаточно средств на балансе!", show_alert=True)
        return
    
    order_id = random.randint(1000000, 9999999)
    
    db.update_balance(callback.from_user.id, -price)
    user = db.get_user(callback.from_user.id)
    
    # Pickup type'ni ko'rsatish
    pickup_type_text = "Прикоп" if pickup_type == "prikop" else "Магнит"
    
    # Pickup type'ni ko'rsatish
    pickup_type_text = "Прикоп" if pickup_type == "prikop" else "Магнит"
    
    weight = product.get("weight", "0.5g")
    pickup_data = PICKUP_INFO.get(district_key, {}).get(weight)
    
    if pickup_data:
        pickup_text = pickup_data["text"]
        images = pickup_data["images"]
    else:
        pickup_text = f"📦 ТОВАР: {product['name']}\n📍 РАЙОН: {district_name}\n🔎 ТИП КЛАДА: {pickup_type_text}"
        images = []
    
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ]
    )
    
    try:
        await callback.message.delete()
    except:
        pass
    
    order_header = f"<b>#{order_id}</b>\n<b>{product['name']} (Ташкент, {district_name})</b>\n<b>Тип: {pickup_type_text}</b>\n\n"
    full_text = order_header + pickup_text + f"\n\n💰 <b>Новый баланс:</b> {user.balance} $"
    
    if images:
        for img_url in images:
            full_text += f"\n{img_url}"
    
    await callback.message.answer(
        full_text,
        reply_markup=back_keyboard,
        parse_mode="HTML"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"🆕 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
                f"👤 {callback.from_user.full_name}\n"
                f"🆔 <code>{callback.from_user.id}</code>\n\n"
                f"📦 {product['name']}\n"
                f"📍 Ташкент, {district_name}\n"
                f"💰 {price} $",
                parse_mode="HTML"
            )
        except:
            pass
    
    await state.clear()


@router.callback_query(F.data == "uzcard_humo")
async def uzcard_humo_handler(callback: CallbackQuery):
    await callback.answer("⚠️ UzCard/Humo временно недоступен.", show_alert=True)


@router.callback_query(F.data.startswith("vbuy_crypto:"))
async def process_buy_crypto(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    
    crypto_type = parts[1]
    item_key = parts[2]
    district_key = parts[3]
    pickup_type = parts[4] if len(parts) > 4 else "prikop"  # prikop yoki magnet
    
    product = PRODUCTS.get(item_key)
    district_name = DISTRICTS.get(district_key, "")
    
    if not product:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    await state.update_data(pickup_type=pickup_type)
    
    price = product['price_usd']
    
    if crypto_type == "ltc":
        crypto_amount_raw = price * LTC_RATE
        crypto_amount = round(crypto_amount_raw, 4)
        crypto_amount_str = format_crypto_amount(crypto_amount_raw, "ltc")
        address = LTC_ADDRESS
        crypto_name = "LTC"
    else:
        crypto_amount_raw = price * BTC_RATE
        crypto_amount = round(crypto_amount_raw, 8)
        crypto_amount_str = format_crypto_amount(crypto_amount_raw, "btc")
        address = BTC_ADDRESS
        crypto_name = "BTC"
    
    application_id = random.randint(1000000, 9999999)
    
    await state.update_data(
        item_key=item_key,
        district_key=district_key,
        price=price,
        crypto_type=crypto_type,
        crypto_name=crypto_name,
        crypto_amount=crypto_amount,
        crypto_amount_str=crypto_amount_str,
        application_id=application_id,
        address=address,
        pickup_type=pickup_type
    )
    
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"vcrypto_confirm:{application_id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"vtype:{item_key}:{district_key}:{pickup_type}")]
        ]
    )
    
    text = f"""https://t.me/BratskiyObmen

<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{price} $</b>

👇 👇 👇
<b>Сумма к оплате: {crypto_amount_str} {crypto_name}</b>
☝️ ☝️ ☝️

⚠️⚠️⚠️ Необходимо перевести точную сумму для оплаты! ⚠️⚠️⚠️
После подтверждения заявки вы получите реквизиты для оплаты! У вас будет 30 минут для того, что бы оплатить. 
Вы можете отправлять сообщения оператору технической поддержки. 
stanislaw - Наш основной аккаунт оператора @BratskiyObmen был заблокирован Telegram. Наш новый аккаунт оператора: @BratskiyObmen

<i>Администрация магазина за действия обменников ответственности не несет!</i>"""
    
    try:
        await callback.message.edit_text(text, reply_markup=confirm_keyboard, parse_mode="HTML")
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=confirm_keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("vcrypto_confirm:"))
async def crypto_confirm_show_address(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id")
    price = data.get("price", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_amount_str = data.get("crypto_amount_str", str(crypto_amount))
    crypto_name = data.get("crypto_name", "LTC")
    crypto_type = data.get("crypto_type", "ltc")
    address = data.get("address", "")
    item_key = data.get("item_key", "")
    district_key = data.get("district_key", "")
    
    # Agar crypto_amount_str bo'lmasa, formatlash
    if not crypto_amount_str or crypto_amount_str == str(crypto_amount):
        crypto_amount_str = format_crypto_amount(crypto_amount, crypto_type)
    
    pickup_type = data.get("pickup_type", "prikop")
    
    paid_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 LTC QR 1", url="https://t.me/BratskiyObmen"),
                InlineKeyboardButton(text="📱 LTC QR 2", url="https://t.me/BratskiyObmen")
            ],
            [InlineKeyboardButton(text="✅ Оплачен", callback_data=f"vcrypto_paid:{application_id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"vtype:{item_key}:{district_key}:{pickup_type}")]
        ]
    )
    
    text = f"""https://t.me/bratskyobmen

<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{price} $</b>

👇 👇 👇
<b>Сумма к оплате: {crypto_amount_str} {crypto_name}</b>

Реквизиты для оплаты: <code>{address}</code>
☝️ ☝️ ☝️



⚠️⚠️⚠️ ПЕРЕВОДИТЬ НАДО ТОЧНУЮ СУММУ! ⚠️⚠️⚠️

Время для оплаты - 30 минут.
Если в течении 5 минут после оплаты ваш платеж не зачислился - отправьте ФОТО квитанции об оплате через кнопку "НАПИСАТЬ СООБЩЕНИЕ" ниже 👇.
stanislaw - Наш основной аккаунт оператора @BratskiyObmen был заблокирован Telegram. Наш новый аккаунт оператора: @BratskiyObmen

<i>Администрация магазина за действия обменников ответственности не несет!</i>"""
    
    try:
        await callback.message.edit_text(text, reply_markup=paid_keyboard, parse_mode="HTML")
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=paid_keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("vcrypto_paid:"))
async def crypto_paid(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id", 0)
    price = data.get("price", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_amount_str = data.get("crypto_amount_str", str(crypto_amount))
    crypto_name = data.get("crypto_name", "LTC")
    crypto_type = data.get("crypto_type", "ltc")
    address = data.get("address", "")
    item_key = data.get("item_key", "")
    district_key = data.get("district_key", "")
    
    # Agar crypto_amount_str bo'lmasa, formatlash
    if not crypto_amount_str or crypto_amount_str == str(crypto_amount):
        crypto_amount_str = format_crypto_amount(crypto_amount, crypto_type)
    
    product = PRODUCTS.get(item_key, {})
    district_name = DISTRICTS.get(district_key, "")
    
    text = f"""<b>Заявка на пополнение #{application_id}</b>
Способ пополнения: {crypto_name}
На баланс: <b>{price} $</b>

Сумма к оплате: {crypto_amount_str} {crypto_name}
Реквизиты для оплаты: <code>{address}</code>



<b>Напишите ваше сообщение</b>
Как ускорить проверку платежа?

1️⃣ Пришлите фото квитанции об оплате. ❗Именно квитанции, чаще всего в приложении банка есть кнопка "получить чек" "открыть квитанцию" и что-то такое Далее необходимо сделать скриншот с экрана телефона или отпрафить файл PDF.
Отправка квитанции в PDF - значительно ускорит проверку.

2️⃣ В некоторых случаях необходимо видео-подтверждение вашей оплаты, как вы заходите в свое банковское приложение на телефоне и показать этот перевод. Видео необходимо оправить сюда в сообщения по заявке."""
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
    
    # Admin bot'ga xabar yuborish
    admin_keyboard = {
        "inline_keyboard": [[
            {
                "text": "✅ Подтвердить",
                "callback_data": f"vcrypto_approve:{callback.from_user.id}:{item_key}:{district_key}:{application_id}"
            },
            {
                "text": "❌ Отклонить",
                "callback_data": f"vcrypto_reject:{callback.from_user.id}:{application_id}"
            }
        ]]
    }
    
    admin_text = (
        f"💰 <b>ЗАЯВКА НА ПОКУПКУ #{application_id}</b>\n\n"
        f"👤 {callback.from_user.full_name}\n"
        f"🆔 <code>{callback.from_user.id}</code>\n\n"
        f"📦 {product.get('name', '')}\n"
        f"📍 {district_name}\n"
        f"💵 {price} $\n"
        f"💎 {crypto_amount_str} {crypto_name}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": admin_id,
                    "text": admin_text,
                    "reply_markup": admin_keyboard,
                    "parse_mode": "HTML"
                }
                await session.post(url, json=payload)
        except Exception as e:
            logger.error(f"Error sending admin message: {e}")
    
    await state.clear()


# Admin handlerlar endi admin_bot.py da


@router.callback_query(F.data.startswith("vdeposit:"))
async def deposit_crypto(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    
    crypto_type = parts[1]
    amount_usd = int(parts[2])
    
    if crypto_type == "ltc":
        crypto_amount_raw = amount_usd * LTC_RATE
        crypto_amount = round(crypto_amount_raw, 4)
        crypto_amount_str = format_crypto_amount(crypto_amount_raw, "ltc")
        address = LTC_ADDRESS
        crypto_name = "LTC"
    else:
        crypto_amount_raw = amount_usd * BTC_RATE
        crypto_amount = round(crypto_amount_raw, 8)
        crypto_amount_str = format_crypto_amount(crypto_amount_raw, "btc")
        address = BTC_ADDRESS
        crypto_name = "BTC"
    
    application_id = random.randint(1000000, 9999999)
    
    await state.update_data(
        deposit_amount=amount_usd,
        crypto_type=crypto_type,
        crypto_name=crypto_name,
        crypto_amount=crypto_amount,
        crypto_amount_str=crypto_amount_str,
        application_id=application_id
    )
    
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"vconfirm:{application_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="vitrina")]
        ]
    )
    
    text_msg = (
        f"<b>Заявка #{application_id}</b>\n"
        f"Способ: {crypto_name}\n"
        f"Сумма: <b>{amount_usd} $</b>\n\n"
        f"<b>К оплате: {crypto_amount_str} {crypto_name}</b>\n\n"
        f"⚠️ Переводите точную сумму!"
    )
    
    try:
        await callback.message.edit_text(
            text_msg,
            reply_markup=confirm_keyboard,
            parse_mode="HTML"
        )
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            text_msg,
            reply_markup=confirm_keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("vconfirm:"))
async def confirm_crypto(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id")
    amount_usd = data.get("deposit_amount", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_amount_str = data.get("crypto_amount_str", str(crypto_amount))
    crypto_name = data.get("crypto_name", "LTC")
    crypto_type = data.get("crypto_type", "ltc")
    
    # Agar crypto_amount_str bo'lmasa, formatlash
    if not crypto_amount_str or crypto_amount_str == str(crypto_amount):
        crypto_amount_str = format_crypto_amount(crypto_amount, crypto_type)
    
    if crypto_type == "ltc":
        address = LTC_ADDRESS
    else:
        address = BTC_ADDRESS
    
    paid_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="vpaid")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="vitrina")]
        ]
    )
    
    await state.update_data(address=address)
    text_msg = (
        f"<b>Заявка #{application_id}</b>\n\n"
        f"<b>К оплате: {crypto_amount_str} {crypto_name}</b>\n\n"
        f"<b>Адрес:</b>\n<code>{address}</code>\n\n"
        f"⏳ Время: 30 минут"
    )
    
    try:
        await callback.message.edit_text(
            text_msg,
            reply_markup=paid_keyboard,
            parse_mode="HTML"
        )
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            text_msg,
            reply_markup=paid_keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data == "vpaid")
async def paid_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    application_id = data.get("application_id", 0)
    amount_usd = data.get("deposit_amount", 0)
    crypto_amount = data.get("crypto_amount", 0)
    crypto_name = data.get("crypto_name", "LTC")
    
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ]
    )
    
    text_msg = (
        f"✅ <b>Заявка #{application_id} принята!</b>\n\n"
        f"💰 Сумма: {amount_usd} $\n\n"
        f"⏳ Ожидайте подтверждения."
    )
    
    try:
        await callback.message.edit_text(
            text_msg,
            reply_markup=back_keyboard,
            parse_mode="HTML"
        )
    except Exception:
        # Agar edit_text ishlamasa (masalan, oldingi xabar photo bo'lsa)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            text_msg,
            reply_markup=back_keyboard,
            parse_mode="HTML"
        )
    await callback.answer()
    
    # Admin bot'ga xabar yuborish
    crypto_amount_str = data.get("crypto_amount_str", str(crypto_amount))
    crypto_type = data.get("crypto_type", "ltc")
    if not crypto_amount_str or crypto_amount_str == str(crypto_amount):
        crypto_amount_str = format_crypto_amount(crypto_amount, crypto_type)
    
    admin_keyboard = {
        "inline_keyboard": [[
            {
                "text": "✅ Подтвердить",
                "callback_data": f"vconfirm_dep:{callback.from_user.id}:{amount_usd}:{application_id}"
            },
            {
                "text": "❌ Отклонить",
                "callback_data": f"vreject_dep:{callback.from_user.id}:{application_id}"
            }
        ]]
    }
    
    admin_text = (
        f"💰 <b>ЗАЯВКА #{application_id}</b>\n\n"
        f"👤 {callback.from_user.full_name}\n"
        f"🆔 <code>{callback.from_user.id}</code>\n\n"
        f"💵 {amount_usd} $\n"
        f"💎 {crypto_amount_str} {crypto_name}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": admin_id,
                    "text": admin_text,
                    "reply_markup": admin_keyboard,
                    "parse_mode": "HTML"
                }
                await session.post(url, json=payload)
        except Exception as e:
            logger.error(f"Error sending admin message: {e}")
    
    await state.clear()


# Admin handlerlar endi admin_bot.py da
