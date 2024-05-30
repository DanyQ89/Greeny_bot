from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from settings_user import Settings
from utils.help_functions import show_user_profile
from data import database
from data.user_form import User
from sqlalchemy import select

from utils.keyboards import premium_settings_kb

premium_height_router = Router(name=__name__)


@premium_height_router.message(Settings.min_height)
async def height_min(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    if user.premium:
        try:
            if msg.text.isdigit() and 99 < int(msg.text) < user.maxHeight:
                user.minHeight = int(msg.text)


                await msg.answer(f'<b>Данные успешно сохранены!</b>')
                await msg.answer('<b>Ваши фильтры пользователей:\n'
                                 f'Возраст: {user.minAge} - {user.maxAge}\n'
                                 f'Рост: {user.minHeight} - {user.maxHeight}</b>', reply_markup=premium_settings_kb())

                await session.commit()
                await state.clear()
            else:
                if msg.text.isdigit():
                    await msg.answer(f'<i>Введите рост от <u>100 до {user.maxHeight - 1} см</u> </i>')
                else:
                    await msg.answer('<i>Введите минимальный рост <u>целым числом</u> </i>')
                await state.set_state(Settings.min_height)
        except Exception as err:
            await msg.answer('<i>Введите минимальный рост <u>целым числом</u> </i>')
            await state.set_state(Settings.min_height)
        finally:
            await session.close()
    else:
        await msg.answer('<i>К сожалению, вы не можете пользоваться опциями Premium-пользователя </i>')

@premium_height_router.message(Settings.max_height)
async def height_min(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    if user.premium:
        try:
            if msg.text.isdigit() and user.minHeight < int(msg.text) < 251:

                user.maxHeight = int(msg.text)

                await msg.answer('<b>Данные успешно сохранены!</b>')
                await msg.answer('<b>Ваши фильтры пользователей:\n'
                                 f'Возраст: {user.minAge} - {user.maxAge}\n'
                                 f'Рост: {user.minHeight} - {user.maxHeight}</b>', reply_markup=premium_settings_kb())

                await session.commit()
                await state.clear()

            else:
                if msg.text.isdigit():
                    await msg.answer(f'<i>Введите рост <u>от {user.minHeight + 1} до 250 см</u> </i>')
                else:
                    await msg.answer('<i>Введите максимальный рост <u>целым числом</u> </i>')
                await state.set_state(Settings.max_height)
        except Exception as err:
            await msg.answer('<i>Введите максимальный рост <u>целым числом</u> </i>')
            await state.set_state(Settings.max_height)
        finally:
            await session.close()
    else:
        await msg.answer('<i>К сожалению, вы не можете пользоваться опциями Premium-пользователя </i>')