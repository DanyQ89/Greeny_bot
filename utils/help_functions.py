from data import database
from data.user_form import User
from aiogram.types import InputMediaPhoto, Message, ReplyKeyboardRemove
from utils.keyboards import main_menu_anketa_kb, main_menu_anketa_kb_premium
from aiogram.fsm.context import FSMContext
from data.change_profile_user import ChangeProfileCallback
from sqlalchemy import select
from math import radians, sin, cos, atan2, sqrt

async def show_user_profile(msg: Message, state: FSMContext):
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    if user:
        name, age, height, photos, main_text, city = user.name, user.age,user.height, user.photos, user.mainText, user.city
        premium_str = '🟢Premium-пользователь🟢\n' if user.premium else ''
        arr = [InputMediaPhoto(media=photos.split()[0], caption=
        f"{premium_str}"
        f'Имя: {name}\n'
        f'Возраст: {age}\n'
        f'Рост: {height}\n'
        f'Город: {city}\n'
        f'{main_text}')]
        for i in photos.split()[1:]:
            arr.append(InputMediaPhoto(media=str(i)))
        await msg.answer('<b> Так выглядит ваш профиль: </b>', reply_markup=ReplyKeyboardRemove())
        await msg.answer_media_group(media=arr)

        if premium_str:
            await msg.answer('<b>Выберите действие: </b>', reply_markup=main_menu_anketa_kb_premium())
        else:
            await msg.answer('<b>Выберите действие: </b>', reply_markup=main_menu_anketa_kb())
        await state.clear()
    else:
        await msg.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')


async def show_user_for_finding(msg: Message, state: FSMContext, userid, km):
    print(1)
    session = await database.create_session()
    another_user = await session.execute(select(User).filter_by(user_id=userid))
    another_user = another_user.scalars().first()
    try:
    # if another_user:
        if km < 1:
            km = f'{round(km * 1000)} м'
        else:
            km = f'{round(km, 1)} км'
        premium = '🟢Premium-пользователь🟢\n' if another_user.premium else ''
        arr_of_photos = [InputMediaPhoto(media=another_user.photos.split()[0], caption=
        f'{premium}'
        f'Имя: {another_user.name}\n'
        f'Возраст: {another_user.age}\n'
        f'Рост: {another_user.height}см\n'
        f'Расстояние от вас: {km}\n'
        f'{another_user.mainText}')]
        for i in another_user.photos.split()[1:]:
            arr_of_photos.append(InputMediaPhoto(media=str(i)))
        await msg.answer_media_group(media=arr_of_photos)
        await state.set_state(Settings.find_profiles)
        await session.commit()
        await session.close()
    except Exception as err:
        print(err)


def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371
    dlat = radians(lat2 - lat1) / 2
    dlon = radians(lon2 - lon1) / 2
    a = sin(dlat) * sin(dlat) + \
        cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon) * sin(dlon)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c
