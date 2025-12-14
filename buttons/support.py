from aiogram.types import InlineKeyboardButton

def support_buttons():
    return [
        InlineKeyboardButton("🧾Поддержка", callback_data="support"),
        InlineKeyboardButton("💱BRATSKIY OBMEN💱", url="https://t.me/bratskiyobmen"),
        InlineKeyboardButton("💸РАБОТА💸", callback_data="support")
    ]
