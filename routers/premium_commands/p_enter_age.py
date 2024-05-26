from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from settings_user import Settings
from data.user_form import User
from data import database
from sqlalchemy import select

premium_age_height_router = Router(name=__name__)


@premium_age_height_router.message(Settings.min_age)
async def age_height(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    try:
        if msg.text.isdigit() and 9 < int(msg.text) < 131:
            user.minAge = int(msg.text)
            await session.commit()
            await msg.answer(f'<b> Введите максимальный возраст пользователя </b>')
            await state.set_state(Settings.max_age)
        else:
            if msg.text.isdigit():
                await msg.answer('<i> Введите возраст <u>от 10 до 130</u> </i>')
            else:
                await msg.answer('<i> Возраст должен быть <u>целым числом</u> </i>')
            await state.set_state(Settings.min_age)
    except Exception as err:
        await msg.answer('<i> Введите минимальный возраст <u>целым числом</u> </i>')
        await state.set_state(Settings.min_age)
    finally:
        await session.close()


@premium_age_height_router.message(Settings.max_age)
async def age_height(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    try:
        if msg.text.isdigit() and 9 < int(msg.text) < 131:
            if user.minAge <= int(msg.text):
                user.maxAge = int(msg.text)
                await session.commit()
                await msg.answer(f'<b> Введите минимальный рост пользователя </b>')
                await state.set_state(Settings.min_height)
            else:
                await msg.answer('<i> Максимальный возраст должен быть не меньше минимального возраста </i>')
                await state.set_state(Settings.max_age)
        else:
            if msg.text.isdigit():
                await msg.answer('<i> Введите возраст <u>от 10 до 130</u> </i>')
            else:
                await msg.answer('<i> Введите максимальный возраст <u>целым числом</u> </i>')
            await state.set_state(Settings.max_age)
    except Exception as err:
        await msg.answer('<i> Введите ваш возраст <u>целым числом</u> </i>')
        await state.set_state(Settings.max_age)
    finally:
        await session.close()
