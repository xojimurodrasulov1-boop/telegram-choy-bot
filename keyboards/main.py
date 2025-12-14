from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛒 Купить Товары", callback_data="products"),
                InlineKeyboardButton(text="💳 Пополнить Баланс", callback_data="balance")
            ],
            [
                InlineKeyboardButton(text="⚠️ Правила", callback_data="rules"),
                InlineKeyboardButton(text="⭐️ Отзывы", callback_data="reviews")
            ],
            [
                InlineKeyboardButton(text="🧾 Поддержка", callback_data="support"),
                InlineKeyboardButton(text="👤 Профиль", callback_data="profile")
            ],
            [
                InlineKeyboardButton(text="💱 BRATSKIY OBMEN 💱", url="https://t.me/bratskiyobmen")
            ]
        ]
    )
    return keyboard


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ]
    )
