from aiogram.types import InlineKeyboardButton

def product_actions_buttons(product_id):
    buttons = [
        InlineKeyboardButton("🛒 Купить", callback_data=f"buy_{product_id}"),
        InlineKeyboardButton("⬅️ Назад", callback_data="back_to_products")
    ]
    return buttons