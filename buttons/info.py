from aiogram import types

async def show_info(call: types.CallbackQuery):
    await call.message.answer(
        "О нашем магазине:\n\n"
        "Мы - надежный поставщик качественных товаров с 2020 года.\n"
        "Наша миссия - предоставить вам лучшие товары по доступным ценам.\n\n"
        "Контакты:\n"
        "Телефон: +998 XX XXX-XX-XX\n"
        "Адрес: г. Ташкент, ул. Примерная, д. 123\n"
        "Время работы: 9:00 - 21:00"
    )
    await call.answer()