from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_balance_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💎 LTC", callback_data="pay_ltc"),
                InlineKeyboardButton(text="🪙 BTC", callback_data="pay_btc")
            ],
            [
                InlineKeyboardButton(text="🎁 PROMOKOD", callback_data="promokod")
            ],
            [
                InlineKeyboardButton(text="💳 Uzcard/Humo", callback_data="pay_card")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
            ]
        ]
    )


def get_crypto_keyboard(crypto_type: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_{crypto_type}")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="balance")
            ]
        ]
    )


def get_card_amounts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="50,000 сум", callback_data="amount_50000"),
                InlineKeyboardButton(text="100,000 сум", callback_data="amount_100000")
            ],
            [
                InlineKeyboardButton(text="200,000 сум", callback_data="amount_200000"),
                InlineKeyboardButton(text="500,000 сум", callback_data="amount_500000")
            ],
            [
                InlineKeyboardButton(text="💵 Другая сумма", callback_data="amount_custom")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="balance")
            ]
        ]
    )


def get_payment_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="balance")
            ]
        ]
    )
