from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from data import database
from utils.keyboards import change_parameters_kb
from data.user_form import User
from db_work import get_user_data

from sqlalchemy import select

show_profile_router = Router(name=__name__)


@show_profile_router.callback_query(F.data == 'show_profile')
async def show_profile(query: CallbackQuery, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(query.from_user.id)))
    user = user.scalars().first()
    # if user:
    #     name, age, height, photos, main_text, city = user.name, user.age, user.height, user.photos, user.mainText, user.city
    #     premium_str = '🟢Premium-пользователь🟢\n' if user.premium else ''
    #     arr = [InputMediaPhoto(media=photos.split()[0], caption=
    #     f"{premium_str}"
    #     f'Имя: {name}\n'
    #     f'Возраст: {age}\n'
    #     f'Рост: {height}\n'
    #     f'Город: {city}\n'
    #     f'{main_text}')]
    #     for i in photos.split()[1:]:
    #         arr.append(InputMediaPhoto(media=str(i)))
    #     await query.message.answer('<b> Так выглядит ваш профиль: </b>', reply_markup=ReplyKeyboardRemove())
    #     await query.message.answer_media_group(media=arr)

    await query.message.edit_text('<b> Прекрасная анкета, что вы хотите изменить? </b>', reply_markup=change_parameters_kb())
    await state.clear()
    await session.close()


async def show_user_by_user_id(query: CallbackQuery,  id):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=id))
    user = user.scalars().first()
    if user:
        name, age, height, photos, main_text = await get_user_data(str(query.message.from_user.id))
        arr = [InputMediaPhoto(media=photos.split()[0], caption=
        f'Имя: {name}\n'
        f'Возраст: {age}\n'
        f'Рост: {height}\n'
        f'{main_text}')]
        for i in photos.split()[1:]:
            arr.append(InputMediaPhoto(media=str(i)))
        await query.message.answer_media_group(media=arr)
    await session.close()