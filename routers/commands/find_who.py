from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto

from data import database
from settings_user import Settings
from utils.buttons import who_kb_buttons, find_who_kb_buttons
from utils.keyboards import find_who_kb, main_menu_anketa_kb
from data import database
from data.user_form import User
from utils.help_functions import show_user_profile

from sqlalchemy import select

who_find_who_router = Router(name=__name__)


@who_find_who_router.message(Settings.who)
async def who_find_who(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    try:
        text = msg.text
        if text in who_kb_buttons:
            if 'Парень' in text:
                user.gender = 'm'
            else:
            # elif 'Девушка' in text:
                user.gender = 'f'
            await session.commit()
            await msg.answer('<b> Кого вы хотите найти? </b>', reply_markup=find_who_kb())
            await state.set_state(Settings.find_who)
        else:
            await msg.answer('<i> Такого варианта ответа не существует </i>')
            await state.set_state(Settings.who)
    except Exception as err:
        await msg.answer('<b> Выберите один из предложенных вариантов ответа </b>')
        await state.set_state(Settings.who)


@who_find_who_router.message(Settings.find_who)
async def find_who_end(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    try:
        text = msg.text
        if text in find_who_kb_buttons:
            if 'Парня' in text:
                user.find_gender = 'm'
            else:
                user.find_gender = 'f'
            await show_user_profile(msg, state)
            await session.commit()
            await state.clear()
        else:
            await msg.answer('<i> Такого варианта ответа не существует </i>')
            await state.set_state(Settings.find_who)
    except Exception as err:
        await msg.answer('<b> Выберите один из предложенных вариантов ответа </b>')
        await state.set_state(Settings.find_who)
    finally:
        await session.close()
