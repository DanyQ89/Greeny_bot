from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from data import database
from data.user_form import User
from sqlalchemy import and_, select
from utils.keyboards import like_or_not_kb, like_or_not_premium_kb, go_home_kb
from utils.help_functions import haversine_distance, send_profile
# from settings_user import Settings
from data.change_profile_user import ChangeSettings as Settings
import pickle
from .base_commands import start
from async_lru import (
    alru_cache,
)

find_profiles_router = Router(name=__name__)


@alru_cache
@find_profiles_router.callback_query(F.data == 'find_profiles')
async def before_f_p(query: CallbackQuery, state: FSMContext):
    await state.set_state(Settings.find_profiles)
    user_id = str(query.from_user.id)
    session = await database.create_session()
    user = await session.execute(select(User).filter_by(user_id=user_id))
    user = user.scalars().first()
    user.last_user_id = ''
    user.last_last_user_id = ''
    premium = user.premium
    await session.commit()
    await session.close()
    if not premium:
        await query.message.answer('<b>Загружаем профили...</b>', reply_markup=like_or_not_kb())
    else:
        await query.message.answer('<b>Загружаем профили...</b>', reply_markup=like_or_not_premium_kb())

    await find_profiles_message(query.message, state, user_id)


@find_profiles_router.message(Settings.find_profiles)
async def find_profiles_message(msg: Message, state: FSMContext, userid=None):
    if not userid:
        userid = str(msg.from_user.id)
    try:
        session = await database.create_session()  # AsyncSession
        user = await session.execute(select(User).filter_by(user_id=userid))
        user = user.scalars().first()
        try:
            arr = pickle.loads(user.arr_of_ids)
        except Exception:
            arr = []

        if not arr:
            try:
                need_user = await session.execute(select(User).filter(and_(User.user_id != user.user_id,
                                                                           User.active == 1,
                                                                           User.gender == user.find_gender,
                                                                           User.find_gender == user.gender,
                                                                           user.minAge <= User.age,
                                                                           User.age <= user.maxAge,
                                                                           user.minHeight <= User.height,
                                                                           User.height <= user.maxHeight)))
                need_user = need_user.scalars().first()
                if not need_user:
                    raise Exception
                else:
                    await get_users_by_distance(userid)
                    await state.set_state(Settings.find_profiles)
                    await find_profiles_message(msg, state, userid)
            except Exception as err:
                await msg.answer('<i> Профили, подходящие по вашим параметрам, пока не найдены, попробуйте позже</i>',
                                 reply_markup=go_home_kb())
        else:
            check = True if (user.last_user_id and arr) else False
            reaction = msg.text
            if reaction == '🏠':
                await start(msg, state)
                # await state.clear()
            # elif check or reaction != 'Выберите действие:':
            else:
                if check:
                    if user.premium:
                        if reaction == '🩷':
                            liked_user = await session.execute(select(User).filter_by(user_id=str(user.last_user_id)))
                            liked_user = liked_user.scalars().first()
                            #
                            #
                            #
                            try:
                                arr_liked = pickle.loads(liked_user.arr_of_liked_ids)
                            except Exception:
                                arr_liked = []
                            arr_liked.append(str(user.user_id))
                            liked_user.arr_of_liked_ids = pickle.dumps(arr_liked)

                            #
                            #
                            #
                        elif reaction == '🤮':
                            pass
                        elif reaction == '❤️‍🔥':
                            if user.premium_like > 0:
                                liked_user = await session.execute(
                                    select(User).filter_by(user_id=str(user.last_user_id)))
                                liked_user = liked_user.scalars().first()
                                user.premium_like -= 1
                                like = 'понравился' if (user.find_gender == 'm') else 'понравилась'

                                await msg.answer('<b>Вы активировали функцию Premium-лайка\n'
                                                 f'Вам {like} @{liked_user.username}</b>')

                                await send_profile(msg, state, user_id=user.user_id, send_to=str(user.last_user_id))
                                await msg.bot.send_message(chat_id=str(user.last_user_id),
                                                           text=f'<b>Вы понравились Premium-пользователю @{user.username}</b>')

                            else:
                                await msg.answer('<b>Вы превысили лимит использования данной функции, вы можете купить'
                                                 ' премиум подписку или ожидать до следующего  дня</b>')
                                arr.insert(0, user.last_user_id)

                        elif reaction == '⏪':
                            arr.insert(0, user.last_user_id)
                            if user.premium_back > 0:
                                user.premium_back -= 1
                                if user.last_last_user_id:
                                    arr.insert(0, user.last_last_user_id)
                                else:
                                    await msg.answer('<i>Вы не можете вернуть профиль назад, не пропустив его</i>')
                            else:
                                await msg.answer('<b>Вы превысили лимит использования данной функции, вы можете купить'
                                                 ' премиум подписку или ожидать до следующего  дня</b>')
                    else:
                        if reaction == '🩷':
                            liked_user = await session.execute(select(User).filter_by(user_id=str(user.last_user_id)))
                            liked_user = liked_user.scalars().first()
                            #
                            #
                            #
                            try:
                                arr_liked = pickle.loads(liked_user.arr_of_liked_ids)
                            except Exception:
                                arr_liked = []

                            arr_liked.append(str(user.user_id))
                            liked_user.arr_of_liked_ids = pickle.dumps(arr_liked)

                            #
                            #
                            #
                        elif reaction == '🤮':
                            pass
                        else:
                            await msg.answer('<i>Такого варианта ответа не существует </i>')
                            arr.insert(0, user.last_user_id)

                user.last_last_user_id = user.last_user_id
                user.last_user_id = arr[0]
                if reaction not in ['🏠', '<b>Выберите действие:</b>']:
                    if len(arr) > 1:
                        arr = arr[1:]
                    else:
                        arr = []
                #
                #
                #
                user.arr_of_ids = pickle.dumps(arr)
                #
                #
                #
                await send_profile(msg, state, user_id=user.last_user_id, send_to=user.user_id)
                await session.commit()
                await session.close()

    except Exception as err:
        print("[ERROR]", err)
        await get_users_by_distance(userid)
        await state.set_state(Settings.find_profiles)
        await find_profiles_message(msg, state, userid)



async def get_users_by_distance(userid):
    session = await database.create_session()
    user = await session.execute(select(User).filter_by(user_id=userid))
    user = user.scalars().first()
    lat1, lon1 = user.coord_x, user.coord_y

    users = await session.execute(select(User).filter(and_(
        User.user_id != user.user_id,
        User.active == 1,
        User.find_gender == user.gender,
        User.gender == user.find_gender,
        user.minAge <= User.age,
        User.age <= user.maxAge,
        user.minHeight <= User.height,
        User.height <= user.maxHeight,
    )))

    users = users.scalars().all()
    users = sorted(users, key=lambda x: haversine_distance(x.coord_x, x.coord_y, lat1, lon1))
    array = [user.user_id for user in users]
    if len(array) > 500:
        array = array[:500]

    user.arr_of_ids = pickle.dumps(array)

    await session.commit()
    await session.close()
