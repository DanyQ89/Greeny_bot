from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class ChangeSettings(StatesGroup):
    lang = State()
    name = State()
    age = State()
    height = State()
    coords = State()
    clear_photo = State()
    photo = State()
    text_of_anketa = State()
    who = State()
    find_who = State()
    find_profiles = State()
    letter_msg = State()


class ChangeProfileCallback(CallbackData, prefix='change'):
    part: str

