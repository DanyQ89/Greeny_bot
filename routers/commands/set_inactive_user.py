from aiogram import Router, F

from data import database
from data.user_form import User
from aiogram.types import InputMediaPhoto, Message, ReplyKeyboardRemove, CallbackQuery

# from settings_user import Settings
from data.change_profile_user import ChangeSettings as Settings
from utils.keyboards import go_home_kb, go_home_edit_text_kb
from aiogram.fsm.context import FSMContext
from data.change_profile_user import ChangeProfileCallback
from sqlalchemy import select


disable_router = Router(name=__name__)

@disable_router.callback_query(F.data == 'disable_profile')
async def set_inactive(query: CallbackQuery, state: FSMContext):
    session = await database.create_session()
    user = await session.execute(select(User).filter_by(user_id=str(query.message.chat.id)))
    user = user.scalars().first()
    user.active = 0
    await query.message.edit_text('<b>Вернуться к поиску?</b>', reply_markup=go_home_edit_text_kb())
    await state.clear()
    await session.commit()
    await session.close()
