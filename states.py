from aiogram.fsm.state import State, StatesGroup


class OrderState(StatesGroup):
    waiting_for_contact = State()
    waiting_for_address = State()
    waiting_for_payment_method = State()


class SupportState(StatesGroup):
    waiting_for_message = State()