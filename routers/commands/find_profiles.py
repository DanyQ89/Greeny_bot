from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from data import database
from data.user_form import User
from sqlalchemy import and_, select
from math import radians, sin, cos, atan2, sqrt
from utils.keyboards import like_or_not_kb
from settings_user import Settings
import pickle

find_profiles_router = Router(name=__name__)

@find_profiles_router.callback_query(F.data == 'find_profiles')
async def before_f_p(query: CallbackQuery, state: FSMContext):
    await state.set_state(Settings.find_profiles)
    await query.message.answer('<b> Загружаем профили... </b>', reply_markup=like_or_not_kb())
    await find_profiles_message(query.message, state, str(query.from_user.id))

@find_profiles_router.message(Settings.find_profiles)
async def find_profiles_message(msg: Message, state: FSMContext, userid=None):
    if not userid:
        userid = str(msg.from_user.id)
    try:
        session = await database.create_session()  # AsyncSession
        user = await session.execute(select(User).filter_by(user_id=userid))
        user = user.scalars().first()
        arr = pickle.loads(user.arr_of_ids)

        if user.last_user_id and arr:
            reaction = msg.text
            if reaction == '🩷':
                await msg.bot.send_message(chat_id=user.last_user_id, text=f'`x Вас лайкнул @{user.username}')



        another_user = await session.execute(select(User).filter_by(user_id=arr[0]))
        another_user = another_user.scalars().first()
        if another_user:
            km = haversine_distance(user.coord_x, user.coord_y, another_user.coord_x, another_user.coord_y)
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
        user.last_user_id = arr[0]
        if len(arr) > 1:
            arr = arr[1:]
        else:
            arr = []
        user.arr_of_ids = pickle.dumps(arr)

        await msg.answer_media_group(media=arr_of_photos)
        await state.set_state(Settings.find_profiles)
        await session.commit()
        await session.close()
    except Exception as err:
        await get_users_by_distance(userid)
        await state.set_state(Settings.find_profiles)
        await find_profiles_message(msg, state, userid)



async def get_users_by_distance(userid):
    session = await database.create_session()
    user = await session.execute(select(User).filter_by(user_id=userid))
    user = user.scalars().first()
    lat1, lon1 = user.coord_x, user.coord_y

    users = await session.execute(
        select(User).filter(and_(User.find_gender == user.gender, User.gender == user.find_gender,
                                 User.user_id != user.user_id)))
    users = users.scalars().all()
    users = sorted(users, key=lambda x: haversine_distance(x.coord_x, x.coord_y, lat1, lon1))
    array = [user.user_id for user in users]
    if len(array) > 500:
        array = array[:500]

    user.arr_of_ids = pickle.dumps(array)

    await session.commit()
    await session.close()


def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371
    dlat = radians(lat2 - lat1) / 2
    dlon = radians(lon2 - lon1) / 2
    a = sin(dlat) * sin(dlat) + \
        cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon) * sin(dlon)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c
