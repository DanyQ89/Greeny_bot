import pickle
import quopri

from aiogram import Router, F

from data import database
from data.user_form import User
from aiogram.types import InputMediaPhoto, Message, ReplyKeyboardRemove, CallbackQuery

# from settings_user import Settings
from data.change_profile_user import ChangeSettings as Settings
from utils.keyboards import (
    main_menu_anketa_kb, main_menu_anketa_kb_premium,
    main_menu_anketa_kb_premium_w_likes, main_menu_anketa_kb_w_likes,
    check_likes_kb, check_likes_final_kb, go_home_kb
)
from aiogram.fsm.context import FSMContext
from data.change_profile_user import ChangeProfileCallback
from sqlalchemy import select
from utils.help_functions import send_user_profile
from utils.buttons import check_likes_kb_button
from .base_commands import start

check_likes_router = Router(name=__name__)


@check_likes_router.callback_query(F.data == 'check_likes')
async def check_likes(query: CallbackQuery, state: FSMContext):
    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(user_id=str(query.message.chat.id)))
    user = user.scalars().first()
    if not user.arr_of_liked_ids:
        await query.message.edit_text('<i> На данный момент список пользователей, которым вы понравились, пуст</i>',
                                      reply_markup=go_home_kb())
    else:
        array_of_liked = pickle.loads(user.arr_of_liked_ids)
        lenn = str(len(array_of_liked))
        if lenn[-1] == '1' and lenn != '11':
            word_user = 'пользователю'
        else:
            word_user = 'пользователям'
        await query.message.edit_text(f'<b> Вы понравились {len(array_of_liked)} {word_user}</b>',
                                      reply_markup=check_likes_final_kb())
    await sess.close()


@check_likes_router.callback_query(F.data == 'check_likes_final')
async def checking_likes(query: CallbackQuery, state: FSMContext):
    await query.message.answer('<b> Загружаем профили... </b>', reply_markup=check_likes_kb())
    await do_the_deal(query.message, state, True)


@check_likes_router.callback_query(F.data == 'come_home')
async def go_home(query: CallbackQuery, state: FSMContext):
    print("here")
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=str(query.from_user.id)))
    user = user.scalars().first()
    await db_session.close()
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
            await query.message.answer('<b> Так выглядит ваш профиль: </b>', reply_markup=ReplyKeyboardRemove())
            await query.message.answer_media_group(media=arr)

            if premium_str:
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_premium_w_likes()
                else:
                    func = main_menu_anketa_kb_premium()
                await query.message.answer('<b> Выберите действие: </b>', reply_markup=func)
            else:
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_w_likes()
                else:
                    func = main_menu_anketa_kb()
                await query.message.answer('<b> Выберите действие: </b>', reply_markup=func)
            await state.clear()
        else:
            await query.message.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')
    except Exception as err:
        await query.message.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')


@check_likes_router.callback_query(F.data == '_come_home')
async def go_home(query: CallbackQuery, state: FSMContext):
    print("YES YES YES")
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=str(query.from_user.id)))
    user = user.scalars().first()
    await db_session.close()
    try:
        if user:
            premium_str = '🟢Premium-пользователь🟢\n' if user.premium else ''
            if premium_str:
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_premium_w_likes()
                else:
                    func = main_menu_anketa_kb_premium()
                await query.message.edit_text('<b> Выберите действие: </b>', reply_markup=func)
            else:
                if user.arr_of_liked_ids:
                    func = main_menu_anketa_kb_w_likes()
                else:
                    func = main_menu_anketa_kb()
                await query.message.edit_text('<b> Выберите действие: </b>', reply_markup=func)
            await state.clear()
        else:
            await query.message.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')
    except Exception as err:
        await query.message.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')


@check_likes_router.message(Settings.check_like)
async def do_the_deal(msg: Message, state: FSMContext, meow=False):
    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(user_id=str(msg.chat.id)))
    user = user.scalars().first()
    array_of_liked = pickle.loads(user.arr_of_liked_ids)
    print(f'{meow=}')
    try:
        if not array_of_liked:
            await msg.answer('<b> Вы просмотрели всех пользователей </b>', reply_markup=go_home_kb())
        else:
            now = array_of_liked[0]
            liked_user = await sess.execute(select(User).filter_by(user_id=now))
            liked_user = liked_user.scalars().first()
            if not meow:
                if msg.text not in check_likes_kb_button:
                    await msg.answer('<i> Такого варианта ответа не существует </i>')
                else:
                    print("stop...")
                    if msg.text in ['🩷', '🤮']:
                        if msg.text == '🩷':
                            word = 'понравился' if (user.find_gender == 'm') else 'понравилась'
                            await msg.answer(f'<b> Вам {word} @{liked_user.username} </b>')
                        if len(array_of_liked) > 1:
                            array_of_liked = array_of_liked[1:]
                            await send_user_profile(msg, state, array_of_liked[0], str(user.user_id))
                            await state.set_state(Settings.check_like)
                        else:
                            array_of_liked = []
                            await msg.answer('<b> Вы просмотрели всех пользователей </b>', reply_markup=go_home_kb())
                        user.arr_of_liked_ids = pickle.dumps(array_of_liked)
                    elif msg.text == '🏠':
                        await start(msg, state)
                        await state.clear()
            else:
                print("else")
                await send_user_profile(msg, state, now, str(user.user_id), meow=True)
                await state.set_state(Settings.check_like)
    except Exception as err:
        print(f"[Error] {err}")
    finally:
        await sess.commit()
        await sess.close()
