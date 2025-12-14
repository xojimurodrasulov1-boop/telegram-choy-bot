from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("🛍️ Купить Товары"),
        KeyboardButton("💰 Баланс"),
        KeyboardButton("⚠️ Правила"),
        KeyboardButton("📞 Поддержка"),
        KeyboardButton("💼 Работа")
    ]
    keyboard.add(*buttons)
    return keyboard

def inline_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🛍️ Купить Товары", callback_data="products"),
        InlineKeyboardButton("💰 Баланс", callback_data="balance"),
        InlineKeyboardButton("⚠️ Правила", callback_data="info"),
        InlineKeyboardButton("📞 Поддержка", callback_data="support"),
        InlineKeyboardButton("💼 Работа", callback_data="work")
    ]
    keyboard.add(*buttons)
    return keyboard

