from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from data.user_form import User
from settings_user import Settings
from utils.buttons import langs_kb_buttons
from utils.keyboards import langs_kb

from sqlalchemy import select

from data import database

lang_name_router = Router(name=__name__)


@lang_name_router.message(Settings.lang)
async def lang_name(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    try:
        if msg.text in langs_kb_buttons:
            user.language = msg.text[1:-1].lower()
            await session.commit()
            await msg.answer('<b>Прекрасный выбор!</b>')
            await msg.answer('<b>Как вас зовут?</b>', reply_markup=ReplyKeyboardRemove())
            await state.set_state(Settings.name)
        else:
            await msg.answer('<i>Выберите язык из <u>предложенных вариантов</u> </i>', reply_markup=langs_kb())
            await state.set_state(Settings.lang)
    except Exception as err:
        await msg.answer('<i>Выберите язык из <u>предложенных вариантов</u> </i>', reply_markup=langs_kb())
        await state.set_state(Settings.lang)

    finally:
        await session.close()
