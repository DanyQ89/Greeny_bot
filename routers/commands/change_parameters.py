from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from data import database
from data.user_form import User
from settings_user import Settings
from utils.keyboards import location_kb, text_of_anketa_kb, photos_kb, yes_or_no_photos_kb, langs_kb
from utils.buttons import text_of_anketa_button, photos_kb_button, show_profile_kb_button
from data.change_profile_user import ChangeProfileCallback as C_B
from data.change_profile_user import ChangeSettings
from utils.help_functions import show_user_profile
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from sqlalchemy import select

change_parameters_router = Router(name=__name__)


@change_parameters_router.callback_query(C_B.filter())
async def change_menu(query: CallbackQuery, state: FSMContext):
    text = query.data.split(':')[1]

    if not any([text == i[1] for i in show_profile_kb_button]):
        await query.message.answer('<i> Выберите один из предложенных вариантов ответа </i>')
    else:
        if text == 'change_name':
            await query.message.edit_text('<b> Введите новое имя для вашего профиля </b>')
            await state.set_state(ChangeSettings.name)

        elif text == 'change_age':
            await query.message.edit_text('<b> Введите новый возраст для вашего профиля </b>')
            await state.set_state(ChangeSettings.age)

        elif text == 'change_height':
            await query.message.edit_text('<b> Введите новый рост для вашего профиля </b>')
            await state.set_state(ChangeSettings.height)

        elif text == 'change_coords':
            await query.message.delete()
            await query.message.answer('<b> Введите обновленное местоположение вашего профиля </b>',
                                       reply_markup=location_kb())
            await state.set_state(ChangeSettings.coords)

        elif text == 'change_main_text':
            await query.message.delete()
            await query.message.answer('<b> Введите новое описание вашего профиля </b>',
                                       reply_markup=text_of_anketa_kb())
            await state.set_state(ChangeSettings.text_of_anketa)

        elif text == 'change_photos':
            await query.message.delete()
            await query.message.answer('<b> Удалить предыдущие фотографии? </b>', reply_markup=yes_or_no_photos_kb())
            await state.set_state(ChangeSettings.clear_photo)

        elif text == 'change_all':
            await query.message.delete()
            db_session = await database.create_session()  # AsyncSession
            user = await db_session.execute(select(User).filter_by(user_id=str(query.message.from_user.id)))
            user = user.scalars().first()
            await db_session.close()
            await query.message.answer('<b> Выберите язык </b>', reply_markup=langs_kb())
            await state.set_state(Settings.lang)


@change_parameters_router.message(ChangeSettings.name)
async def change_name(msg: Message, state: FSMContext):
    try:
        db_session = await database.create_session()  # AsyncSession
        user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
        user = user.scalars().first()
        name = msg.text
        if 1 < len(name) < 21:
            user.name = name
            await db_session.commit()
            await db_session.close()
            await msg.answer('<b> Имя успешно обновлено! </b>')
            await show_user_profile(msg, state)
        else:
            if len(name) < 2:
                await msg.answer('<i> Слишком короткое имя </i>')
                await state.set_state(ChangeSettings.name)
            else:
                await msg.answer('<i> Слишком длинное имя </i>')
                await state.set_state(ChangeSettings.name)
    except Exception as err:
        await msg.answer('<i> Введите ваше имя текстом </i>')
        await state.set_state(ChangeSettings.name)


@change_parameters_router.message(ChangeSettings.age)
async def change_age(msg: Message, state: FSMContext):
    try:
        db_session = await database.create_session()  # AsyncSession
        user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
        user = user.scalars().first()
        age = int(msg.text)
        if 9 < age < 131:
            user.age = age
            await db_session.commit()
            await db_session.close()
            await msg.answer('<b> Возраст успешно обновлен! </b>')
            await show_user_profile(msg, state)
        else:
            await msg.answer('<i> Введите возраст <u>от 10 до 130</u> </i>')
            await state.set_state(ChangeSettings.age)
    except Exception as err:
        await msg.answer('<i> Введите ваш возраст <u>целым числом</u> </i>')
        await state.set_state(ChangeSettings.age)


@change_parameters_router.message(ChangeSettings.height)
async def change_height(msg: Message, state: FSMContext):
    try:
        db_session = await database.create_session()  # AsyncSession
        user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
        user = user.scalars().first()

        height = int(msg.text)
        if 99 < height < 251:
            user.height = height
            await db_session.commit()
            await db_session.close()
            await msg.answer('<b> Рост успешно обновлен! </b>')
            await show_user_profile(msg, state)
        else:
            await db_session.close()
            await msg.answer('<i> Введите рост <u>от 100 до 250 см</u> </i>')
            await state.set_state(ChangeSettings.height)

    except Exception as err:
        await msg.answer('<i> Введите ваш рост <u>целым числом</u> </i>')
        await state.set_state(ChangeSettings.height)


@change_parameters_router.message(ChangeSettings.coords)
async def change_coords(msg: Message, state: FSMContext):
    try:
        db_session = await database.create_session()  # AsyncSession
        user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
        user = user.scalars().first()

        user.coord_x, user.coord_y = msg.location.latitude, msg.location.longitude
        async with Nominatim(user_agent='tg_bot',
                             adapter_factory=AioHTTPAdapter) as geolocator:
            loc = await geolocator.reverse((user.coord_x, user.coord_y), exactly_one=True)
            address = loc.raw['address']
            user.city = address.get('city', 'none')
        await db_session.commit()
        await db_session.close()
        await msg.answer('<b> Координаты успено обновлены! </b>')
        await show_user_profile(msg, state)
    except Exception as err:
        await msg.answer('<i> Укажите ваши координаты с помощью кнопки </i>', reply_markup=location_kb())
        await state.set_state(ChangeSettings.coords)


@change_parameters_router.message(ChangeSettings.text_of_anketa)
async def change_main_text(msg: Message, state: FSMContext):
    try:
        db_session = await database.create_session()  # AsyncSession
        user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
        user = user.scalars().first()

        text = msg.text
        lenn = len(msg.text)
        if 3 <= lenn <= 600:
            if text in text_of_anketa_button:
                text = ''
            user.mainText = text
            await db_session.commit()
            await db_session.close()
            await msg.answer('<b> Текст анкеты успешно обновлен! </b>')
            await show_user_profile(msg, state)
        else:
            await db_session.close()
            if 0 < lenn < 3:
                await msg.answer('<i> Текст анкеты слишком короткий </i>')
            elif lenn > 600:
                await msg.answer('<i> Текст анкеты слишком длинный </i>')
            await state.set_state(ChangeSettings.text_of_anketa)
    except Exception:
        await msg.answer('<i> Напишите что-то о себе или выберите кнопку "Не хочу ничего писать" </i>')
        await state.set_state(ChangeSettings.text_of_anketa)


@change_parameters_router.message(ChangeSettings.clear_photo)
async def ask_before_photos(msg: Message, state: FSMContext):
    try:
        text = msg.text
        if 'Да' in text:
            db_session = await database.create_session()  # AsyncSession
            user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
            user = user.scalars().first()
            user.photos = ''
            await db_session.commit()
            await db_session.close()
        await msg.answer('<b> Пришлите свои фотографии (до 5, присылайте по одной фотографии за раз) </b>',
                         reply_markup=photos_kb())
        await state.set_state(ChangeSettings.photo)
    except Exception as err:
        await msg.answer('<i> Выберите один из предложенных вариантов ответа </i>', reply_markup=yes_or_no_photos_kb())
        await state.set_state(ChangeSettings.clear_photo)


@change_parameters_router.message(ChangeSettings.photo)
async def change_photos(msg: Message, state: FSMContext):
    try:
        db_session = await database.create_session()  # AsyncSession
        user = await db_session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
        user = user.scalars().first()
        photos = msg.photo
        if photos:
            photo_id = photos[0].file_id
            from bot import bot
            await bot.download(photo_id)
            lenn = len(user.photos.split() if user.photos else [])
            if not lenn:
                user.photos += photo_id
            elif lenn < 5:
                user.photos += f' {photo_id}'
            await db_session.commit()
            await db_session.close()

            if lenn + 1 > 4:
                await msg.answer('<b> Отлично! Фотографии обновлены </b>')
                await show_user_profile(msg, state)
            else:
                await msg.answer(f'<b> Фотография №{lenn + 1} из 5, загрузить еще? </b>',
                                 reply_markup=photos_kb())
                await state.set_state(ChangeSettings.photo)
        elif msg.text in photos_kb_button:
            await db_session.close()
            if user.photos:
                await msg.answer('<b> Отлично! Фотографии сохранены </b>')
                await show_user_profile(msg, state)
            else:
                await msg.answer('<b> Ваш профиль не может содержать <i>ни одной</i> фотографии </b>')
                await state.set_state(ChangeSettings.photo)
    except Exception as err:
        await msg.answer('<b> Пришлите фотографию </b>')
        await state.set_state(ChangeSettings.photo)
