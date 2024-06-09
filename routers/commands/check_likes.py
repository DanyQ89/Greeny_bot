import pickle

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from data import database
# from settings_user import Settings
from data.change_profile_user import ChangeSettings as Settings
from data.user_form import User
from utils.buttons import check_likes_kb_button
from utils.help_functions import send_profile, show_user_profile
from utils.keyboards import (
    main_menu_anketa_kb, main_menu_anketa_kb_premium,
    main_menu_anketa_kb_premium_w_likes, main_menu_anketa_kb_w_likes,
    check_likes_kb, check_likes_final_kb, go_home_kb
)
from .base_commands import start

check_likes_router = Router(name=__name__)


@check_likes_router.callback_query(F.data == 'check_likes')
async def check_likes(query: CallbackQuery, state: FSMContext):
    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(user_id=str(query.message.chat.id)))
    user = user.scalars().first()
    if not user.arr_of_liked_ids:
        await query.message.edit_text('<i>На данный момент список пользователей, которым вы понравились, пуст</i>',
                                      reply_markup=go_home_kb())
    else:
        try:
            array_of_liked = pickle.loads(user.arr_of_liked_ids)
        except Exception:
            array_of_liked = []
        lenn = str(len(array_of_liked))
        if lenn[-1] == '1' and lenn != '11':
            word_user = 'пользователю'
        else:
            word_user = 'пользователям'
        await query.message.edit_text(f'<b>Вы понравились {len(array_of_liked)} {word_user}</b>',
                                      reply_markup=check_likes_final_kb())
    await sess.close()


@check_likes_router.callback_query(F.data == 'check_likes_final')
async def checking_likes(query: CallbackQuery, state: FSMContext):
    await query.message.answer('<b>Загружаем профили...</b>', reply_markup=check_likes_kb())
    await do_the_deal(query.message, state, True)


@check_likes_router.callback_query(F.data == 'come_home')
async def go_home(query: CallbackQuery, state: FSMContext):
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=str(query.from_user.id)))
    user = user.scalars().first()
    await db_session.close()
    try:
        if user:
            await show_user_profile(query.message, state, user.user_id)

        else:
            await query.message.answer('<i>Здесь какая-то ошибка, введите "/start" </i>')
    except Exception as err:
        await query.message.answer('<i>Здесь какая-то ошибка, введите "/start" </i>')


@check_likes_router.callback_query(F.data == '_come_home')
async def go_home(query: CallbackQuery, state: FSMContext):
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=str(query.from_user.id)))
    user = user.scalars().first()
    user.active = 1
    await state.clear()

    try:
        if user:
            try:
                arr = pickle.loads(user.arr_of_liked_ids)
            except Exception:
                arr = []
            if user.premium:
                if arr:
                    func = main_menu_anketa_kb_premium_w_likes()
                else:
                    func = main_menu_anketa_kb_premium()
            else:
                if arr:
                    func = main_menu_anketa_kb_w_likes()
                else:
                    func = main_menu_anketa_kb()
            await query.message.edit_text('<b>Выберите действие:</b>', reply_markup=func)
        else:
            await query.message.answer('<i>Здесь какая-то ошибка, введите "/start" </i>')
        await db_session.commit()
        await db_session.close()
    except Exception as err:
        await query.message.answer('<i>Здесь какая-то ошибка, введите "/start" </i>')
        await db_session.commit()
        await db_session.close()


@check_likes_router.message(Settings.check_like)
async def do_the_deal(msg: Message, state: FSMContext, meow=False):
    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(user_id=str(msg.chat.id)))
    user = user.scalars().first()
    try:
        array_of_liked = pickle.loads(user.arr_of_liked_ids)
    except Exception:
        array_of_liked = []
    try:
        if not array_of_liked:
            await msg.answer('<b>Вы просмотрели всех пользователей</b>', reply_markup=go_home_kb())
        else:
            now = array_of_liked[0]
            liked_user = await sess.execute(select(User).filter_by(user_id=now))
            liked_user = liked_user.scalars().first()
            if not meow:
                if msg.text not in check_likes_kb_button:
                    await msg.answer('<i>Такого варианта ответа не существует </i>')
                else:
                    if msg.text in ['🩷', '🤮']:
                        if msg.text == '🩷':
                            word = 'понравился' if (user.find_gender == 'm') else 'понравилась'
                            await msg.answer(f'<b>Вам {word} @{liked_user.username}</b>')
                            await send_profile(msg, state, user_id=user.user_id, send_to=liked_user.user_id)
                            await msg.bot.send_message(chat_id=liked_user.user_id,
                                                       text=f'<b>У вас взаимная симпатия с пользователем @{user.username}</b>')

                        if len(array_of_liked) < 2:
                            array_of_liked = []
                            await msg.answer('<b>Вы просмотрели всех пользователей</b>', reply_markup=go_home_kb())
                        else:
                            array_of_liked = array_of_liked[1:]

                            await send_profile(msg, state, user_id=array_of_liked[0], send_to=user.user_id)

                        user.arr_of_liked_ids = pickle.dumps(array_of_liked)
                    elif msg.text == '🏠':
                        await start(msg, state)
                        await state.clear()
            else:
                await send_profile(msg, state, now, user.user_id)
                await state.set_state(Settings.check_like)
    except Exception as err:
        pass
    finally:
        await sess.commit()
        await sess.close()
