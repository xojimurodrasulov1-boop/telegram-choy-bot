from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Купить товар", callback_data="vitrina"),
                InlineKeyboardButton(text="💳 Пополнить б...", callback_data="balance")
            ],
            [
                InlineKeyboardButton(text="❗️ Правила", callback_data="rules"),
                InlineKeyboardButton(text="🧾 Поддержка", url="https://t.me/StoreTashkent_support")
            ],
            [
                InlineKeyboardButton(text="💸 BRATSKIY ОБМЕН 💸", url="https://t.me/BratskiyObmen")
            ],
            [
                InlineKeyboardButton(text="💰 РАБОТА 💰", url="https://t.me/StoreTashkent_support")
            ],
            [
                InlineKeyboardButton(text="📋 Последние з...", callback_data="last_orders"),
                InlineKeyboardButton(text="⭐ Отзывы", callback_data="reviews")
            ],
            [
                InlineKeyboardButton(text="🤖 Подключить своего бота", callback_data="connect_bot")
            ]
        ]
    )
    return keyboard


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ]
    )


def get_reply_keyboard() -> ReplyKeyboardMarkup:
    """Reply klaviatura - Меню tugmasi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Меню")]],
        resize_keyboard=True
    )
    return keyboard


def get_menu_commands_keyboard() -> ReplyKeyboardMarkup:
    """Menu tugmasini bosganda ko'rsatiladigan buyruqlar"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/list")],
            [KeyboardButton(text="/support")],
            [KeyboardButton(text="/rules")],
            [KeyboardButton(text="/info")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_commands_list_keyboard() -> InlineKeyboardMarkup:
    """Bot buyruqlarini chat ichida ko'rsatish uchun inline keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="cmd_start")],
            [InlineKeyboardButton(text="Витрина товаров", callback_data="cmd_list")],
            [InlineKeyboardButton(text="Обратная связь", callback_data="cmd_support")],
            [InlineKeyboardButton(text="Правила работы", callback_data="cmd_rules")],
            [InlineKeyboardButton(text="Информация о магазине", callback_data="cmd_info")]
        ]
    )
    return keyboard
