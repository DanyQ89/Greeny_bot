from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from data import database
from data.user_form import User
from sqlalchemy import and_, select
from utils.keyboards import like_or_not_kb, like_or_not_premium_kb
from utils.help_functions import haversine_distance, show_user_for_finding, send_user_profile
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
        meow = False
        check = True if (user.last_user_id and arr) else False
        reaction = msg.text
        print(arr, reaction)
        if check and (reaction == '🏠'):
            await start(msg, state)
            await state.clear()
        # elif check or reaction != 'Выберите действие:':
        else:
            if check:
                if user.premium:
                    if reaction == '🩷':
                        print("why")
                        liked_user = await session.execute(select(User).filter_by(user_id=str(user.last_user_id)))
                        liked_user = liked_user.scalars().first()
                        print("MEOW")
                        #
                        #
                        #
                        arr_liked = []
                        if liked_user.arr_of_liked_ids:
                            arr_liked = pickle.loads(liked_user.arr_of_liked_ids)
                        print(11)
                        arr_liked.append(str(user.user_id))
                        print(22)
                        liked_user.arr_of_liked_ids = pickle.dumps(arr_liked)

                        #
                        #
                        #
                        await msg.answer('meow 🩷')
                    # elif reaction == '💌':
                    #     await msg.answer('<b> Напишите сообщение пользователю: </b>')
                    #     await state.set_state(Settings.letter_msg)
                    #     await like_w_letter(msg, state, userid, user.last_user_id)
                    elif reaction == '🤮':
                        meow = True
                    elif reaction == '❤️‍🔥' and user.premium_like >= 1:
                        liked_user = await session.execute(select(User).filter_by(user_id=str(user.last_user_id)))
                        liked_user = liked_user.scalars().first()
                        user.premium_like -= 1
                        like = 'понравился' if (user.find_gender == 'm') else 'понравилась'
                        await msg.answer('<b> Вы активировали функцию Premium-лайка\n'
                                         f'Вам {like} @{liked_user.username}</b>')
                        await send_user_profile(msg, state, userid, str(user.last_user_id))
                    elif reaction == '❤️‍🔥':
                        await msg.answer('<b> Вы превысили лимит использования данной функции, вы можете купить'
                                         ' премиум подписку или ожидать до следующего  дня </b>')
                    elif reaction == '⏪':
                        if user.last_last_user_id:
                            arr.insert(0, user.last_user_id)
                            arr.insert(0, user.last_last_user_id)
                        else:
                            await msg.answer('<i> Вы не можете вернуть профиль назад, не пропустив его</i>')
                else:
                    if reaction == '🩷':
                        liked_user = await session.execute(select(User).filter_by(user_id=str(user.last_user_id)))
                        liked_user = liked_user.scalars().first()
                        #
                        #
                        #
                        arr_liked = []
                        if liked_user.arr_of_liked_ids:
                            arr_liked = pickle.loads(liked_user.arr_of_liked_ids)
                        print(1)
                        arr_liked.append(str(user.user_id))
                        print(2)
                        liked_user.arr_of_liked_ids = pickle.dumps(arr_liked)

                        #
                        #
                        #
                        await msg.answer('meow 🩷')
                    # elif reaction == '💌':
                    #     await msg.answer('<b> Напишите сообщение пользователю: </b>')
                    #     await state.set_state(Settings.letter_msg)
                    #     await like_w_letter(msg, state, userid, user.last_user_id)
                    elif reaction == '🤮':
                        meow = True
                    elif reaction == '❤️‍🔥':
                        await msg.answer('<b> Функция супер лайка доступна только для пользователей с премиумом </b>')
            user.last_last_user_id = user.last_user_id
            user.last_user_id = arr[0]
            if len(arr) > 1 and reaction != '🏠' and reaction != ' Выберите действие:':
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
            print(arr)
            print(100)
            await show_user_for_finding(msg, state, str(user.last_user_id), user.coord_x, user.coord_y)
            await session.commit()
            await session.close()
            print("No error")

    except Exception as err:
        print("[ERROR]", err)
        await get_users_by_distance(userid)
        await state.set_state(Settings.find_profiles)
        await find_profiles_message(msg, state, userid)


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

    users = await session.execute(select(User).filter(and_(
        User.user_id != user.user_id,
        User.find_gender == user.gender,
        User.gender == user.find_gender,
        user.minAge <= User.age,
        User.age <= user.maxAge,
        user.minHeight <= User.height,
        User.height <= user.maxHeight
    )))

    users = users.scalars().all()
    users = sorted(users, key=lambda x: haversine_distance(x.coord_x, x.coord_y, lat1, lon1))
    array = [user.user_id for user in users]
    if len(array) > 500:
        array = array[:500]

    user.arr_of_ids = pickle.dumps(array)

    await session.commit()
    await session.close()
