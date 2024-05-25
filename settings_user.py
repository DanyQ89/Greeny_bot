from aiogram.fsm.state import StatesGroup, State


class Settings(StatesGroup):
    lang = State()
    name = State()
    age = State()
    height = State()
    coords = State()
    photo = State()
    text_of_anketa = State()
    who = State()
    find_who = State()
    find_profiles = State()
