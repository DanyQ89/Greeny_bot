from data import database
from data.user_form import User
from aiogram.types import InputMediaPhoto, Message, ReplyKeyboardRemove
from utils.keyboards import main_menu_anketa_kb, main_menu_anketa_kb_premium
from aiogram.fsm.context import FSMContext
from data.change_profile_user import ChangeProfileCallback
from sqlalchemy import select

async def show_user_profile(msg: Message, state: FSMContext):
    db_session = await database.create_session()  # AsyncSession
    user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()

    if user:
        name, age, height, photos, main_text, city = user.name, user.age,user.height, user.photos, user.mainText, user.city
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
        await msg.answer('<b> Так выглядит ваша анкета: </b>', reply_markup=ReplyKeyboardRemove())
        await msg.answer_media_group(media=arr)

        if premium_str:
            await msg.answer('<b>Выберите действие: </b>', reply_markup=main_menu_anketa_kb_premium())
        else:
            await msg.answer('<b>Выберите действие: </b>', reply_markup=main_menu_anketa_kb())
        await state.clear()
    else:
        await msg.answer('<i> Здесь какая-то ошибка, введите "/start" </i>')
