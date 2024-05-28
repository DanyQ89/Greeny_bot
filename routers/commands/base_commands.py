from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data import database
from data.user_form import User
from settings_user import Settings
from utils.keyboards import langs_kb
from sqlalchemy import select
from utils.help_functions import show_user_profile

router = Router(name=__name__)


@router.message(CommandStart())
@router.callback_query(F.data == 'come_home')
async def start(msg: Message, state: FSMContext):
    db_sess = await database.create_session()  # AsyncSession
    user = await db_sess.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    try:
        if not user.find_gender:
            raise Exception
        await show_user_profile(msg, state)

    except Exception as err:
        if not user or not user.username:
            user = User()
            user.user_id = str(msg.from_user.id)
            user.username = str(msg.from_user.username)
            db_sess.add(user)
            await db_sess.commit()
        await msg.answer('<b> Выберите язык </b>', reply_markup=langs_kb())
        await state.set_state(Settings.lang)

    finally:
        await db_sess.close()
