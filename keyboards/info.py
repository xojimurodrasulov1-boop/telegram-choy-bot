from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_USERNAME


def get_info_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Kanalimiz", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
            ],
            [
                InlineKeyboardButton(text="🍵 Choy haqida", callback_data="about_tea")
            ],
            [
                InlineKeyboardButton(text="🏪 Do'kon haqida", callback_data="about_shop")
            ],
            [
                InlineKeyboardButton(text="📜 Foydalanish shartlari", callback_data="terms")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")
            ]
        ]
    )
    return keyboard


def get_tea_info_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🍃 Yashil choy", callback_data="info_green_tea")
            ],
            [
                InlineKeyboardButton(text="🫖 Qora choy", callback_data="info_black_tea")
            ],
            [
                InlineKeyboardButton(text="🌿 O'simlik choyi", callback_data="info_herbal_tea")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_info")
            ]
        ]
    )
    return keyboard
