from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from buttons.products import products_buttons
from buttons.info import info_buttons
from buttons.support import support_buttons

def main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💰Купить Товары", callback_data="products"),
        InlineKeyboardButton("💳Пополнить Баланс", callback_data="balance"),
        InlineKeyboardButton("⚠️Правила", callback_data="info"),
        InlineKeyboardButton("🧾Поддержка", callback_data="support"),
        InlineKeyboardButton("💸РАБОТА💸", callback_data="support"),
        InlineKeyboardButton("💱BRATSKIY OBMEN💱", callback_data="change"),
        InlineKeyboardButton("⭐️Отзывы", callback_data="change")
    )
    return keyboard

