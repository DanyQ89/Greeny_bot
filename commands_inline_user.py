from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State


class CommandsInline(StatesGroup):
    command = State()


class PremiumInline(CallbackData, prefix='buy_premium'):
    days: int
