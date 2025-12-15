from aiogram.fsm.state import State, StatesGroup


class CaptchaStates(StatesGroup):
    waiting_for_captcha = State()


class DepositStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_screenshot = State()
    waiting_for_crypto_amount = State()
    waiting_for_tx_hash = State()
    waiting_for_deposit_amount = State()


class OrderStates(StatesGroup):
    selecting_product = State()
    confirming_order = State()
    entering_address = State()
    entering_phone = State()


class SupportStates(StatesGroup):
    waiting_for_message = State()
