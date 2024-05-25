from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from data import database
from data.user_form import User
from sqlalchemy import and_, select
from math import radians, sin, cos, atan2, sqrt
from utils.keyboards import like_or_not_kb
from settings_user import Settings

find_profiles_router = Router(name=__name__)


@find_profiles_router.callback_query(F.data == 'find_profiles')
async def to_find_profiles(query: CallbackQuery, state: FSMContext):
    await find_profiles(query.message, state)


@find_profiles_router.message(Settings.find_profiles)
async def find_profiles(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    arr = user.arr_of_ids

    if user.last_user_id:
        reaction = msg.text
        if reaction == '🩷':
            user_liked = await session.execute(select(User).filter_by(id=user.last_user_id))
            user_liked = user_liked.scalar().first()
            await msg.bot.send_message(chat_id=user_liked.user_id, text=f'Вас лайкнул @{user.username}')
    if arr:
        another_user = session.query(User).get(arr[0])

        if another_user:
            arr_of_photos = [InputMediaPhoto(media=another_user.photos.split()[0], caption=
            f'Имя: {another_user.name}\n'
            f'Возраст: {another_user.age}\n'
            f'Рост: {another_user.height}\n'
            f'{another_user.mainText}')]
            for i in another_user.photos.split()[1:]:
                arr_of_photos.append(InputMediaPhoto(media=str(i)))
            await msg.answer('<b> Загружаем профили... </b>', reply_markup=like_or_not_kb())
            await msg.answer_media_group(media=arr_of_photos)
            await state.set_state(Settings.find_profiles)
        user.last_user_id = arr[0]
        if len(arr):
            arr = arr[1:]
        else:
            arr = []
        user.arr_of_ids = bytes(arr)
        await session.commit()
        await session.close()
    else:
        await get_users_by_distance(msg.from_user.id)
        await find_profiles(msg, state)


async def get_users_by_distance(userid: int):
    session = await database.create_session()
    user = await session.execute(select(User).filter_by(user_id=userid))
    user = user.scalars().first()
    lat1, lon1 = user.coord_x, user.coord_y

    users = session.query(User).filter(and_(User.find_gender == user.gender, User.gender == user.find_gender,
                                            User.user_id != user.user_id)).limit(500).all()
    users = sorted(users, key=lambda x: haversine_distance(x.coord_x, x.coord_y, lat1, lon1))
    user.arr_of_ids = bytes([user.id for user in users])
    await session.commit()



def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371
    dlat = radians(lat2 - lat1) / 2
    dlon = radians(lon2 - lon1) / 2
    a = sin(dlat) * sin(dlat) + \
        cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon) * sin(dlon)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c
