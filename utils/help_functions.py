from aiogram import Router

from data import database
from data.user_form import User
from aiogram.types import InputMediaPhoto, Message, ReplyKeyboardRemove

# from settings_user import Settings
from data.change_profile_user import ChangeSettings as Settings
from utils.keyboards import (main_menu_anketa_kb, main_menu_anketa_kb_premium,
                             main_menu_anketa_kb_premium_w_likes, main_menu_anketa_kb_w_likes)
from aiogram.fsm.context import FSMContext
from data.change_profile_user import ChangeProfileCallback
from sqlalchemy import select
from math import radians, sin, cos, atan2, sqrt

help_functions_router = Router(name=__name__)


async def show_user_profile(msg: Message, state: FSMContext, userid=None):
    db_session = await database.create_session()  # AsyncSession
    if userid:
        user = await db_session.execute(select(User).filter_by(user_id=userid))
    else:
        user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    await state.clear()
    try:
        if user:
            name, age, height, photos, main_text, city = user.name, user.age, user.height, user.photos, user.mainText, user.city

            # premium_str = '🟢Premium-пользователь🟢\n' if user.premium else ''
            premium_str = True if user.premium else False
            if premium_str:
                arr = [InputMediaPhoto(media=photos.split()[0], caption=
                f""
                f'<b>🟢 {name}, {age}\n'
                f'🌿 {height} см\n'
                f'📍 {city}\n'
                f'{"🖊️" + main_text if main_text else ''}</b>')]
            else:
                arr = [InputMediaPhoto(media=photos.split()[0], caption=
                f'{name}, {age}\n'
                f'🌿 {height} см\n'
                f'📍 {city}\n'
                f'{"🖊️" + main_text if main_text else ''}')]

            if photos.count(' '):
                for i in photos.split()[1:]:
                    arr.append(InputMediaPhoto(media=str(i)))

            await msg.answer('<b>Так выглядит ваш профиль:</b>', reply_markup=ReplyKeyboardRemove())
            await msg.answer_media_group(media=arr)

            if premium_str:
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_premium_w_likes()
                else:
                    func = main_menu_anketa_kb_premium()
            else:
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_w_likes()
                else:
                    func = main_menu_anketa_kb()
            await msg.answer('<b>Выберите действие:</b>', reply_markup=func)
        else:
            await msg.answer('<i>Здесь какая-то ошибка, введите "/start" </i>')
    except Exception as err:
        await msg.answer('<i>Здесь какая-то ошибка, введите "/start" </i>')


async def send_profile(msg, state, user_id, send_to):
    try:
        db_session = await database.create_session()  # AsyncSession
        user = await db_session.execute(select(User).filter_by(user_id=user_id))
        user = user.scalars().first()

        to_user = await db_session.execute(select(User).filter_by(user_id=send_to))
        to_user = to_user.scalars().first()

        name, age, height, photos, main_text, city = user.name, user.age, user.height, user.photos, user.mainText, user.city
        km = haversine_distance(user.coord_x, user.coord_y, to_user.coord_x, to_user.coord_y)
        if km < 1:
            km = f'{round(km * 1000)} м'
        else:
            km = f'{round(km, 1)} км'

        # premium_str = '🟢<b>Premium-пользователь</b>🟢\n' if user.premium else ''
        premium_str = True if user.premium else False
        if premium_str:
            arr = [InputMediaPhoto(media=photos.split()[0], caption=
            f""
            f'<b>🟢 {name}, {age}\n'
            f'🌿 {height} см\n'
            f'📍 {km}\n'
            f'{"🖊️" + main_text if main_text else ''}</b>')]
        else:
            arr = [InputMediaPhoto(media=photos.split()[0], caption=
            f'{name}, {age}\n'
            f'🌿 {height} см\n'
            f'📍 {km}\n'
            f'{"🖊️" + main_text if main_text else ''}')]

        for i in photos.split()[1:]:
            arr.append(InputMediaPhoto(media=str(i)))
        await msg.bot.send_media_group(chat_id=send_to, media=arr)
        await db_session.close()
    except Exception as err:
        await msg.answer('<i>Здесь какая-то ошибка, введите "/start" </i>')


def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371
    dlat = radians(lat2 - lat1) / 2
    dlon = radians(lon2 - lon1) / 2
    a = sin(dlat) * sin(dlat) + \
        cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon) * sin(dlon)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c
