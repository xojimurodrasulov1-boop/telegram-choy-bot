from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def balance_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("💳 Пополнить баланс", callback_data="top_up_balance"),
        InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
    ]
    keyboard.add(*buttons)
    return buttons


