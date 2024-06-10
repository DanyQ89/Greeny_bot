from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from data import database
from data.user_form import User
from sqlalchemy import and_, select
<<<<<<< HEAD
from math import radians, sin, cos, atan2, sqrt
from utils.keyboards import like_or_not_kb
from settings_user import Settings
=======
from utils.keyboards import like_or_not_kb, like_or_not_premium_kb
from utils.help_functions import haversine_distance, show_user_for_finding, send_user_profile
# from settings_user import Settings
from data.change_profile_user import ChangeSettings as Settings
import pickle
from .base_commands import start
>>>>>>> be33045550988345cd2253a86af969908e9ad8ee

find_profiles_router = Router(name=__name__)

@find_profiles_router.callback_query(F.data == 'find_profiles')
<<<<<<< HEAD
async def to_find_profiles(query: CallbackQuery, state: FSMContext):
    await find_profiles(query.message, state)


@find_profiles_router.message(Settings.find_profiles)
async def find_profiles(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
=======
async def before_f_p(query: CallbackQuery, state: FSMContext):
    await state.set_state(Settings.find_profiles)
    user_id = str(query.from_user.id)
    session = await database.create_session()
    user = await session.execute(select(User).filter_by(user_id=user_id))
>>>>>>> be33045550988345cd2253a86af969908e9ad8ee
    user = user.scalars().first()
    if not user.premium:
        await query.message.answer('<b> Загружаем профили... </b>', reply_markup=like_or_not_kb())
    else:
        await query.message.answer('<b> Загружаем профили... </b>', reply_markup=like_or_not_premium_kb())

<<<<<<< HEAD
    if user.last_user_id:
        reaction = msg.text
        if reaction == '🩷':
            user_liked = await session.execute(select(User).filter_by(id=user.last_user_id))
            user_liked = user_liked.scalar().first()
            await msg.bot.send_message(chat_id=user_liked.user_id, text=f'Вас лайкнул @{user.username}')
    if arr:
        another_user = session.query(User).get(arr[0])
=======
    await find_profiles_message(query.message, state, user_id)

@find_profiles_router.message(Settings.find_profiles)
async def find_profiles_message(msg: Message, state: FSMContext, userid=None):
    if not userid:
        userid = str(msg.from_user.id)
    try:
        session = await database.create_session()  # AsyncSession
        user = await session.execute(select(User).filter_by(user_id=userid))
        user = user.scalars().first()
        arr = pickle.loads(user.arr_of_ids)
        meow = None

        if user.last_user_id and arr:
            reaction = msg.text
            if reaction == '🩷':
                await msg.answer('meow 🩷')
            elif reaction == '💌':
                await msg.answer('<b> Напишите сообщение пользователю: </b>')
                await state.set_state(Settings.letter_msg)
                await like_w_letter(msg, state, userid, user.last_user_id)
            elif reaction == '🤮':
                meow = True
            elif reaction == '❤️‍🔥':
                await msg.answer('<b> Сообщение отправлено <b/>')
                await send_user_profile(msg, state, userid, user.last_user_id)
            elif reaction == '⏪':
                arr.insert(0, user.last_user_id)
            elif reaction == '🏠':
                await start(msg, state)
>>>>>>> be33045550988345cd2253a86af969908e9ad8ee

        user.last_user_id = arr[0]


        if len(arr) > 1:
            arr = arr[1:]
        else:
            arr = []
        user.arr_of_ids = pickle.dumps(arr)

        await show_user_for_finding(msg, state, str(user.last_user_id), user.coord_x, user.coord_y)

        await session.commit()
        await session.close()
<<<<<<< HEAD
    else:
        await get_users_by_distance(msg.from_user.id)
        await find_profiles(msg, state)
=======

    except Exception as err:
        await get_users_by_distance(userid)
        await state.set_state(Settings.find_profiles)
        await find_profiles_message(msg, state, userid)
>>>>>>> be33045550988345cd2253a86af969908e9ad8ee


@find_profiles_router.message(Settings.letter_msg)
async def like_w_letter(msg: Message, state: FSMContext, userid, chatid):
    try:
        letter = msg.text
        lenn = len(letter)
        if 2 < lenn < 100:
            await msg.answer('<b>Сообщение отправлено</b>')

            # add user to all

            await find_profiles_message(msg, state, userid)
        else:
            if lenn < 3:
                await msg.answer('<i> Сообщение должно быть <u>от 3</u> символов</i>')
            else:
                await msg.answer('<i> Сообщение должно быть <u>до 100</u> символов</i>')
            await state.set_state(Settings.letter_msg)
    except Exception as err:
        await msg.answer('<i> Напишите сообщение <u>текстом</u> </i>')
        await state.set_state(Settings.letter_msg)


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


