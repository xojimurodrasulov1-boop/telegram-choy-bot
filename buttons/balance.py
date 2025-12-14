# buttons/balance.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def balance_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("LTC", callback_data="ltc"),
        InlineKeyboardButton("BTC", callback_data="btc"),
        InlineKeyboardButton("PROMOKOD", callback_data="promokod")
    )
    return kb
