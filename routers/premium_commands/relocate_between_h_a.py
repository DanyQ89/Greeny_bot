from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from settings_user import Settings
from data.user_form import User
from data import database
from sqlalchemy import select
from commands_inline_user import PremiumSettings
from utils.keyboards import premium_settings_kb, main_menu_anketa_kb_premium
from data.database import create_session

premium_relocate_router = Router(name=__name__)

@premium_relocate_router.callback_query(F.data == 'premium_settings')
async def premium_relocate(query: CallbackQuery, state: FSMContext):
    session = await create_session()
    user = await session.execute(select(User).filter_by(user_id=str(query.message.chat.id)))
    user = user.scalars().first()

    # если chat_id и user_id станут разными то ошибка будет здесь

    await query.message.edit_text('<b> Ваши фильтры пользователей:\n'
                     f'Возраст: {user.minAge} - {user.maxAge}\n'
                     f'Рост: {user.minHeight} - {user.maxHeight}</b>', reply_markup=premium_settings_kb())

    # await query.message.edit_text('<b> Выберите дополнительный параметр: </b>', reply_markup=premium_settings_kb())

@premium_relocate_router.callback_query(PremiumSettings.filter())
async def premium_settings(query: CallbackQuery, state: FSMContext):
    data = query.data.split(':')[1]
    if data == 'set_height_min':
        await query.message.edit_text('<b> Введите минимальный рост пользователя </b>')
        await state.set_state(Settings.min_height)
    elif data == 'set_age_min':
        await query.message.edit_text('<b> Введите минимальный возраст пользователя </b>')
        await state.set_state(Settings.min_age)
    elif data == 'set_height_max':
        await query.message.edit_text('<b> Введите максимальный рост пользователя </b>')
        await state.set_state(Settings.max_height)
    elif data == 'set_age_max':
        await query.message.edit_text('<b> Введите максимальный возраст пользователя </b>')
        await state.set_state(Settings.max_age)
    elif data == 'come_home':
        await query.message.edit_text('<b> Выберите действие: </b>',
                                      reply_markup=main_menu_anketa_kb_premium())
        await state.clear()