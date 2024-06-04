from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from data import database
from utils.keyboards import change_parameters_kb
from data.user_form import User

from sqlalchemy import select

show_profile_router = Router(name=__name__)


@show_profile_router.callback_query(F.data == 'show_profile')
async def show_profile(query: CallbackQuery, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(query.from_user.id)))
    user = user.scalars().first()

    await query.message.edit_text('<b>Прекрасная анкета, что вы хотите изменить?</b>',
                                  reply_markup=change_parameters_kb())
    await state.clear()
    await session.close()

