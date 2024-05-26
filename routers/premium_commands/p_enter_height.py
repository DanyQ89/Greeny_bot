from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from settings_user import Settings
from utils.help_functions import show_user_profile
from data import database
from data.user_form import User
from sqlalchemy import select

premium_height_router = Router(name=__name__)


@premium_height_router.message(Settings.min_height)
async def height_min(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    try:
        if msg.text.isdigit() and 99 < int(msg.text) < 251:
            user.minHeight = int(msg.text)
            await session.commit()
            await session.close()
            await msg.answer('<b> Укажите максимальный рост пользователя </b>')
            await state.set_state(Settings.max_height)
        else:
            if msg.text.isdigit():
                await msg.answer('<i> Введите рост от 100 см до 250 см </i>')
            else:
                await msg.answer('<i> Введите ваш рост <u>целым числом</u> </i>')
            await state.set_state(Settings.min_height)
    except Exception as err:
        await msg.answer('<i> Введите ваш рост <u>целым числом</u> </i>')
        await state.set_state(Settings.min_height)


@premium_height_router.message(Settings.max_height)
async def height_min(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    try:
        if msg.text.isdigit() and 99 < int(msg.text) < 251:
            if user.minHeight < int(msg.text):
                user.maxHeight = int(msg.text)
                await msg.answer('<i> Данные успешно сохранены </i>')
                await show_user_profile(msg, state)
                await session.commit()
                await state.clear()
            else:
                await msg.answer('<i> Максимальный рост должен быть <u>больше</u> минимального роста </i>')
                await state.set_state(Settings.max_height)
        else:
            if msg.text.isdigit():
                await msg.answer('<i> Введите рост от 100 см до 250 см </i>')
            else:
                await msg.answer('<i> Введите ваш рост <u>целым числом</u> </i>')
            await state.set_state(Settings.max_height)
    except Exception as err:
        await msg.answer('<i> Введите ваш рост <u>целым числом</u> </i>')
        await state.set_state(Settings.max_height)