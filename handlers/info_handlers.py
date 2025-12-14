from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import SHOP_NAME, SHOP_DESCRIPTION, CHANNEL_USERNAME
from keyboards.info import get_info_keyboard, get_tea_info_keyboard

router = Router()


@router.message(F.text == "ℹ️ Ma'lumot")
async def show_info(message: Message):
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
    
    await message.answer(
        info_text,
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_info")
async def back_to_info(callback: CallbackQuery):
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
    
    await callback.message.edit_text(
        info_text,
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "about_tea")
async def about_tea(callback: CallbackQuery):
    tea_text = """
🍵 <b>Choy haqida qiziqarli ma'lumotlar</b>

━━━━━━━━━━━━━━━━━━━━
Choy - dunyoda suvdan keyin eng ko'p iste'mol qilinadigan ichimlik!

🌿 <b>Choyning foydalari:</b>
• Antioksidantlarga boy
• Immunitetni mustahkamlaydi
• Konsentratsiyani oshiradi
• Stress va tashvishni kamaytiradi
• Yurak salomatligini yaxshilaydi

☕ <b>Kuniga 3-4 piyola choy ichish tavsiya etiladi</b>
━━━━━━━━━━━━━━━━━━━━

Choy turlari haqida ko'proq bilib oling:
"""
    
    await callback.message.edit_text(
        tea_text,
        reply_markup=get_tea_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "info_green_tea")
async def info_green_tea(callback: CallbackQuery):
    text = """
🍃 <b>Yashil Choy</b>

━━━━━━━━━━━━━━━━━━━━
Yashil choy - eng foydali choy turlaridan biri!

<b>Xususiyatlari:</b>
• Yuqori antioksidant tarkibi
• Metabolizmni tezlashtiradi
• Vazn yo'qotishga yordam beradi
• Tishlarni mustahkamlaydi
• Teri sog'lig'ini yaxshilaydi

<b>Tayyorlash:</b>
🌡 Suv harorati: 70-80°C
⏱ Dam berish: 2-3 daqiqa

💡 <i>Maslahat: Yashil choyni qaynoq suv bilan tayyorlamang, 
achchiq ta'm chiqadi!</i>
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_tea_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "info_black_tea")
async def info_black_tea(callback: CallbackQuery):
    text = """
🫖 <b>Qora Choy</b>

━━━━━━━━━━━━━━━━━━━━
Qora choy - eng mashhur va sevimli choy turi!

<b>Xususiyatlari:</b>
• Kuchli va xushbo'y ta'm
• Energiya beradi
• Hazm qilishni yaxshilaydi
• Yurak uchun foydali
• Kofein tarkibiga ega

<b>Tayyorlash:</b>
🌡 Suv harorati: 90-100°C
⏱ Dam berish: 3-5 daqiqa

💡 <i>Maslahat: Sut yoki limon bilan 
ichilsa mazasi yanada yaxshi!</i>
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_tea_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "info_herbal_tea")
async def info_herbal_tea(callback: CallbackQuery):
    text = """
🌿 <b>O'simlik Choyi</b>

━━━━━━━━━━━━━━━━━━━━
O'simlik choyi - tabiat in'omi!

<b>Xususiyatlari:</b>
• 100% tabiiy
• Kofeinsiz
• Turli xil o'simliklardan
• Davolash xususiyatlari
• Tinchlantiruvchan ta'sir

<b>Mashhur turlari:</b>
🍃 Yalpiz choyi - hazm uchun
🌼 Qalampir gul choyi - tinchlanish uchun
🍯 Zanjabil choyi - immunitet uchun
🌸 Gullar choyi - sog'liq uchun

<b>Tayyorlash:</b>
🌡 Suv harorati: 95-100°C
⏱ Dam berish: 5-10 daqiqa
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_tea_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "about_shop")
async def about_shop(callback: CallbackQuery):
    shop_text = f"""
🏪 <b>Do'konimiz haqida</b>

━━━━━━━━━━━━━━━━━━━━
<b>{SHOP_NAME}</b>

Biz 2020-yildan buyon O'zbekiston bo'ylab eng sifatli 
va tabiiy choylarni yetkazib beramiz.

🎯 <b>Bizning maqsadimiz:</b>
Har bir uyga sifatli choy olib kelish!

📦 <b>Bizning xizmatlar:</b>
• Tezkor yetkazib berish (1-3 kun)
• Sifat kafolati
• Qulay to'lov usullari
• Professional maslahat

📞 <b>Aloqa:</b>
📱 Telegram: {CHANNEL_USERNAME}
🕐 Ish vaqti: 09:00 - 21:00

━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        shop_text,
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "terms")
async def show_terms(callback: CallbackQuery):
    terms_text = """
📜 <b>Foydalanish shartlari</b>

━━━━━━━━━━━━━━━━━━━━
<b>1. Umumiy qoidalar</b>
• Botdan foydalanish bepul
• Ro'yxatdan o'tish majburiy emas

<b>2. Buyurtma berish</b>
• Minimal buyurtma summasi: 20,000 so'm
• To'lov oldindan amalga oshiriladi
• Buyurtma 1-3 kun ichida yetkaziladi

<b>3. To'lov</b>
• To'lov faqat so'm valyutasida
• Karta orqali to'lov qabul qilinadi

<b>4. Qaytarish</b>
• Mahsulot sifatsiz bo'lsa qaytariladi
• Qaytarish 3 kun ichida amalga oshiriladi

<b>5. Maxfiylik</b>
• Shaxsiy ma'lumotlaringiz himoyalangan
• Uchinchi shaxslarga berilmaydi
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        terms_text,
        reply_markup=get_info_keyboard(),
        parse_mode="HTML"
    )
