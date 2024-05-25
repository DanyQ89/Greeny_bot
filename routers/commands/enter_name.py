import random

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from settings_user import Settings
from db_work import get_user_by_id
name_age_router = Router()
from data import database
from data.user_form import User
from sqlalchemy import select

@name_age_router.message(Settings.name)
async def name_age(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    komps_for_name = ['Прекрасное', 'Чудесное', 'Великолепное', 'Превосходное', 'Красивое']
    try:
        if 2 <= len(msg.text) <= 20:
            user.name = msg.text
            await session.commit()
            await session.close()
            await msg.answer(f'<b> {random.choice(komps_for_name)} имя! </b>')
            await msg.answer('<b> Сколько вам лет? </b>', reply_markup=ReplyKeyboardRemove())
            await state.set_state(Settings.age)
        else:
            await msg.answer('<i> Введите ваше имя длиной <u>от 2 до 20 символов</u> </i>')
            await state.set_state(Settings.name)
    except Exception as err:
        await msg.answer('<i> Введите ваше имя длиной <u>от 2 до 20 символов</u> </i>')
        await state.set_state(Settings.name)
