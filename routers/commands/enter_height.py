from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from settings_user import Settings
from utils.keyboards import location_kb
from data import database
from data.user_form import User

height_coords_router = Router(name=__name__)
from sqlalchemy import select


@height_coords_router.message(Settings.height)
async def height_coords(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    try:
        if msg.text.isdigit() and 99 < int(msg.text) < 251:
            user.height = int(msg.text)
            user.minHeight = 100
            user.maxHeight = 250
            await session.commit()
            await session.close()
            await msg.answer('<b>Укажите ваши координаты\n(они будут зашифрованы и не смогут быть просмотрены)</b>',
                             reply_markup=location_kb())
            await state.set_state(Settings.coords)
        else:
            if msg.text.isdigit():
                await msg.answer('<i>Введите рост от 100 см до 250 см </i>')
            else:
                await msg.answer('<i>Введите ваш рост <u>целым числом</u> </i>')
            await state.set_state(Settings.height)
    except Exception as err:
        await msg.answer('<i>Введите ваш рост <u>целым числом</u> </i>')
        await state.set_state(Settings.height)
