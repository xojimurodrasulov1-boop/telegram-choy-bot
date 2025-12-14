from aiogram import types
from keyboards.main_buttons import main_keyboard

async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer(
        "Добро пожаловать в наш магазин! 🛍️\n\n"
        "Здесь вы можете приобрести качественные товары по доступным ценам.\n"
        "Выберите действие из меню ниже:",
        reply_markup=main_keyboard()
    )