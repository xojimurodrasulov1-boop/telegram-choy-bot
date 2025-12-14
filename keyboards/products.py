from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.products_data import PRODUCTS, DISTRICTS


def get_products_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, product in PRODUCTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{product['name']}",
                callback_data=f"show_{key}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_detail_keyboard(product_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy_{product_key}")
            ],
            [
                InlineKeyboardButton(text="🔙 К товарам", callback_data="products")
            ]
        ]
    )


def get_districts_keyboard(product_key: str) -> InlineKeyboardMarkup:
    buttons = []
    for key, district in DISTRICTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{district['name']} (+{district['delivery_price']:,} сум)",
                callback_data=f"district_{key}_{product_key}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"show_{product_key}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_order_keyboard(product_key: str, district_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить заказ",
                    callback_data=f"confirm_{product_key}_{district_key}"
                )
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="products")
            ]
        ]
    )
