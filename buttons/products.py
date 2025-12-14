from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.products import PRODUCTS
from data.districts import DISTRICTS

def products_keyboard(district_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Add product buttons
    buttons = []
    for product_id, product in PRODUCTS.items():
        if district_id is None or product['district'] == district_id:
            buttons.append(
                InlineKeyboardButton(
                    f"{product['name']} - {product['price']}$",
                    callback_data=f"product_{product_id}"
                )
            )
    
    keyboard.add(*buttons)
    
    # Add district buttons if no district selected
    if district_id is None:
        district_buttons = []
        for district_id, district in DISTRICTS.items():
            district_buttons.append(
                InlineKeyboardButton(
                    district['name'],
                    callback_data=f"district_{district_id}"
                )
            )
        keyboard.add(*district_buttons)
    
    # Add back button
    keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
    
    return keyboard