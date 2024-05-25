from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot import bot
from settings_user import Settings
from utils.buttons import photos_kb_button
from utils.keyboards import text_of_anketa_kb, photos_kb
from data.user_form import User
from data import database

from sqlalchemy import select

photo_text_router = Router(name=__name__)



@photo_text_router.message(Settings.photo)
async def photo_text(msg: Message, state: FSMContext):
    try:
        session = await database.create_session()  # AsyncSession
        user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
        user = user.scalars().first()
        if msg.photo:
            photo_id = msg.photo[0].file_id
            await msg.bot.download(photo_id)
            if user.photos:
                lenn = user.photos.count(' ') + 1
            else:
                lenn = 0

            if not lenn:
                user.photos += photo_id
            elif lenn < 5:
                user.photos += f' {photo_id}'
            await session.commit()

            if lenn + 1 > 4:
                await msg.answer('<b> Отлично! Фотографии сохранены </b>')
                await msg.answer('<b> Напишите немного о себе </b>', reply_markup=text_of_anketa_kb())
                await state.set_state(Settings.text_of_anketa)
            else:
                await msg.answer(f'<b> Фотография №{lenn + 1} из 5, загрузить еще? </b>',
                                 reply_markup=photos_kb())
                await state.set_state(Settings.photo)

        elif msg.text in photos_kb_button:
            if user.photos:
                await msg.answer('<b> Отлично! Фотографии сохранены </b>')
                await msg.answer('<b> Напишите немного о себе </b>', reply_markup=text_of_anketa_kb())
                await state.set_state(Settings.text_of_anketa)
            else:
                await msg.answer('<i> Анкета не может содержать <u>ни одной</u> фотографии </i>',
                             reply_markup=ReplyKeyboardRemove())

                await state.set_state(Settings.photo)
    except Exception as err:
        # try:
        #     if msg.text in photos_kb_button:
        #         if user.photos:
        #             await msg.answer('<b> Отлично! Фотографии сохранены </b>')
        #             await msg.answer('<b> Напишите немного о себе </b>', reply_markup=text_of_anketa_kb())
        #             await state.set_state(Settings.text_of_anketa)
        #         else:
        #             await msg.answer('<i> Анкета не может содержать <u>ни одной</u> фотографии </i>',
        #                              reply_markup=ReplyKeyboardRemove())
        #
        #             await state.set_state(Settings.photo)
        # except Exception as err:
        #     # await msg.answer(str(err))
        await msg.answer('<b> Пришлите фотографию </b>')
        await state.set_state(Settings.photo)

# import asyncio
# asyncio.run(photo_text(Message, FSMContext))
