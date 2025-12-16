from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏪 Витрина", callback_data="vitrina"),
                InlineKeyboardButton(text="💳 Пополнить Баланс", callback_data="balance")
            ],
            [
                InlineKeyboardButton(text="⚠️ Правила", callback_data="rules"),
                InlineKeyboardButton(text="⭐️ Отзывы", callback_data="reviews")
            ],
            [
                InlineKeyboardButton(text="🧾 Поддержка", url="https://t.me/StoreTashkent_support"),
                InlineKeyboardButton(text="👤 Профиль", callback_data="profile")
            ]
        ]
    )
    return keyboard
