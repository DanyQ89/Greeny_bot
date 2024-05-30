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


async def show_user_profile(msg: Message, state: FSMContext):
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    try:
        if user:
            name, age, height, photos, main_text, city = user.name, user.age, user.height, user.photos, user.mainText, user.city
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
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_premium_w_likes()
                else:
                    func = main_menu_anketa_kb_premium()
                await msg.answer('<b> Выберите действие: </b>', reply_markup=func)
            else:
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_w_likes()
                else:
                    func = main_menu_anketa_kb()
                await msg.answer('<b> Выберите действие: </b>', reply_markup=func)
            await state.clear()
        else:
            await msg.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')
    except Exception as err:
        await msg.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')


async def show_user_for_finding(msg: Message, state: FSMContext, userid, user_coord_x, user_coord_y):
    session = await database.create_session()
    another_user = await session.execute(select(User).filter_by(user_id=userid))
    another_user = another_user.scalars().first()
    try:
        # if another_user:
        km = haversine_distance(user_coord_x, user_coord_y, another_user.coord_x, another_user.coord_y)
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


async def send_user_profile(msg: Message, state: FSMContext, userid, chatid, meow=False):
    """
    :param userid: another_user
    :param chatid: your account
    """
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=userid))
    user = user.scalars().first()
    try:
        to_user = await db_session.execute(select(User).filter_by(user_id=chatid))
        to_user = to_user.scalars().first()
        if user:
            name, age, height, photos, main_text, city = user.name, user.age, user.height, user.photos, user.mainText, user.city
            km = haversine_distance(user.coord_x, user.coord_y, to_user.coord_x, to_user.coord_y)
            if km < 1:
                km = f'{round(km * 1000)}м'
            else:
                km = f'{round(km, 1)}км'
            premium_str = '🟢Premium-пользователь🟢\n' if user.premium else ''
            arr = [InputMediaPhoto(media=photos.split()[0], caption=
            f"{premium_str}"
            f'Имя: {name}\n'
            f'Возраст: {age}\n'
            f'Рост: {height}\n'
            f'Расстояние от вас: {km}\n'
            f'{main_text}')]
            for i in photos.split()[1:]:
                arr.append(InputMediaPhoto(media=str(i)))
            await msg.bot.send_media_group(chat_id=chatid, media=arr)
            if not meow:
                if premium_str:
                    await msg.bot.send_message(chat_id=userid,
                                               text=f'<b> Вы понравились Premium-пользователю @{to_user.username}</b>')
                else:
                    await msg.bot.send_message(chat_id=userid,
                                               text=f'<b> У вас взаимная симпатия с пользователем @{to_user.username} </b>')
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
