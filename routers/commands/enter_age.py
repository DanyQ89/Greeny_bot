from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from settings_user import Settings
from data.user_form import User
from data import database
from sqlalchemy import select

age_height_router = Router(name=__name__)


@age_height_router.message(Settings.age)
async def age_height(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    try:
        if msg.text.isdigit() and 9 < int(msg.text) < 131:
            user.age = int(msg.text)
            await session.commit()
            await msg.answer('<b> Введите ваш рост в сантиметрах</b>', reply_markup=ReplyKeyboardRemove())
            await state.set_state(Settings.height)
        else:
            if msg.text.isdigit():
                await msg.answer('<i> Введите возраст <u>от 10 до 130</u> </i>')
            else:
                await msg.answer('<i> Введите ваш возраст <u>целым числом</u> </i>')
            await state.set_state(Settings.age)
    except Exception as err:
        await msg.answer('<i> Введите ваш возраст <u>целым числом</u> </i>')
        await state.set_state(Settings.age)
