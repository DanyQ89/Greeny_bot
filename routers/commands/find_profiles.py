from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from data import database
from data.user_form import User
from sqlalchemy import and_, select
from utils.keyboards import like_or_not_kb, like_or_not_premium_kb
from utils.help_functions import haversine_distance, show_user_for_finding
from settings_user import Settings
import pickle

find_profiles_router = Router(name=__name__)

@find_profiles_router.callback_query(F.data == 'find_profiles')
async def before_f_p(query: CallbackQuery, state: FSMContext):
    await state.set_state(Settings.find_profiles)
    user_id = str(query.from_user.id)
    session = await database.create_session()
    user = await session.execute(select(User).filter_by(user_id=user_id))
    user = user.scalars().first()
    if not user.premium:
        await query.message.answer('<b> Загружаем профили... </b>', reply_markup=like_or_not_kb())
    else:
        await query.message.answer('<b> Загружаем профили... </b>', reply_markup=like_or_not_premium_kb())

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

        if user.last_user_id and arr:
            reaction = msg.text
            if reaction == '🩷':
                await msg.bot.send_message(chat_id=user.last_user_id, text=f'Вас лайкнул @{user.username}')
            elif reaction == '':
                pass



        user.last_user_id = arr[0]
        if len(arr) > 1:
            arr = arr[1:]
        else:
            arr = []
        user.arr_of_ids = pickle.dumps(arr)
        print(0)
        km = haversine_distance(user.coord_x, user.coord_y, another_user.coord_x, another_user.coord_y)
        await show_user_for_finding(msg, state, str(user.last_user_id), km)
        print(5)
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


