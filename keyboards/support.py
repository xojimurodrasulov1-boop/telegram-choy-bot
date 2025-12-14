from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Написать оператору", callback_data="write_support")
            ],
            [
                InlineKeyboardButton(text="📞 Связаться напрямую", url="https://t.me/choy_support")
            ],
            [
                InlineKeyboardButton(text="❓ FAQ", callback_data="faq")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
            ]
        ]
    )


def get_faq_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚚 Доставка", callback_data="faq_delivery")
            ],
            [
                InlineKeyboardButton(text="💳 Оплата", callback_data="faq_payment")
            ],
            [
                InlineKeyboardButton(text="🔄 Возврат", callback_data="faq_return")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="support")
            ]
        ]
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
