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


@check_likes_router.message(Settings.check_like)
async def do_the_deal(msg: Message, state: FSMContext, meow=False):
    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(user_id=str(msg.chat.id)))
    user = user.scalars().first()
    array_of_liked = pickle.loads(user.arr_of_liked_ids)
    now= array_of_liked[0]
    liked_user = await sess.execute(select(User).filter_by(user_id=now))
    liked_user = liked_user.scalars().first()
    if not array_of_liked:
        await msg.answer('<b> Вы просмотрели всех пользователей </b>', reply_markup=go_home_kb())
    else:
        if not meow:
            if msg.text not in check_likes_kb_button:
                await msg.answer('<i> Такого варианта ответа не существует </i>')
            else:
                if msg.text == '🩷':
                    word = 'понравился' if (user.find_gender == 'm') else 'понравилась'
                    await msg.answer(f'<b> Вам {word} @{liked_user.username} </b>')
                    await send_user_profile(msg, state, str(user.user_id), now)
                    await state.set_state(Settings.check_like)
                elif msg.text == '🏠':
                    await start(msg, state)
                    await state.clear()
        else:
            await send_user_profile(msg, state, now, str(user.user_id))
            await state.set_state(Settings.check_like)
    await sess.close()