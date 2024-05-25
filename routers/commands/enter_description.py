from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from settings_user import Settings
from utils.buttons import text_of_anketa_button
from utils.keyboards import who_kb

from data.user_form import User
from data import database

from sqlalchemy import select

text_who_router = Router(name=__name__)


@text_who_router.message(Settings.text_of_anketa)
async def text_who(msg: Message, state: FSMContext):
    session = await database.create_session()  # AsyncSession
    user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    try:
        text = msg.text
        lenn = len(msg.text)
        if 3 <= lenn <= 600:
            if text not in text_of_anketa_button:
                await msg.answer('<b> Интересное описание анкеты! </b>')
            else:
                text = ''
            user.mainText = text
            await session.commit()
            await session.close()
            await msg.answer('<b> Укажите свой пол </b>', reply_markup=who_kb())
            await state.set_state(Settings.who)
        else:
            if 0 < lenn < 3:
                await msg.answer('<i> Текст анкеты слишком короткий </i>')
            elif lenn > 600:
                await msg.answer('<i> Текст анкеты слишком длинный </i>')
            await state.set_state(Settings.text_of_anketa)

    except Exception as err:
        await msg.answer('<i> Напишите что-то о себе или выберите кнопку "Не хочу ничего писать" </i>')
        await state.set_state(Settings.text_of_anketa)

