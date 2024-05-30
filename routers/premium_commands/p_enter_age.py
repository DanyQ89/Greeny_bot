from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from settings_user import Settings
from data.user_form import User
from data import database
from sqlalchemy import select

from utils.help_functions import show_user_profile
from utils.keyboards import premium_settings_kb

premium_age_height_router = Router(name=__name__)


@premium_age_height_router.message(Settings.min_age)
async def age_height(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    if user.premium:
        try:
            if msg.text.isdigit() and 9 < int(msg.text) < user.maxAge:
                user.minAge = int(msg.text)


                await msg.answer(f'<b>Данные успешно сохранены!</b>')
                await msg.answer('<b>Ваши фильтры пользователей:\n'
                                 f'Возраст: {user.minAge} - {user.maxAge}\n'
                                 f'Рост: {user.minHeight} - {user.maxHeight}</b>', reply_markup=premium_settings_kb())

                await session.commit()
                await state.clear()
            else:
                if msg.text.isdigit():
                    await msg.answer(f'<i>Введите возраст <u>от 10 до {user.maxAge - 1}</u> </i>')
                else:
                    await msg.answer('<i>Введите минимальный возраст <u>целым числом</u> </i>')
                await state.set_state(Settings.min_age)
        except Exception as err:
            await msg.answer('<i>Введите минимальный возраст <u>целым числом</u> </i>')
            await state.set_state(Settings.min_age)
        finally:
            await session.close()
    else:
        await msg.answer('<i>К сожалению, вы не можете пользоваться опциями Premium-пользователя </i>')

@premium_age_height_router.message(Settings.max_age)
async def age_height(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    if user.premium:
        try:
            if msg.text.isdigit() and user.minAge < int(msg.text) < 131:

                user.maxAge = int(msg.text)

                await msg.answer('<b>Данные успешно сохранены!</b>')
                await msg.answer('<b>Ваши фильтры пользователей:\n'
                                 f'Возраст: {user.minAge} - {user.maxAge}\n'
                                 f'Рост: {user.minHeight} - {user.maxHeight}</b>', reply_markup=premium_settings_kb())

                await session.commit()
                await state.clear()
            else:
                if msg.text.isdigit():
                    await msg.answer(f'<i>Введите возраст <u>от {user.minAge + 1} до 130</u> </i>')
                else:
                    await msg.answer('<i>Введите максимальный возраст <u>целым числом</u> </i>')
                await state.set_state(Settings.max_age)
        except Exception as err:
            await msg.answer('<i>Введите максимальный возраст <u>целым числом</u> </i>')
            await state.set_state(Settings.max_age)
        finally:
            await session.close()
    else:
        await msg.answer('<i>К сожалению, вы не можете пользоваться опциями Premium-пользователя </i>')