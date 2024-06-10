from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from settings_user import Settings
from utils.keyboards import photos_kb, location_kb
from data import database
from data.user_form import User
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from sqlalchemy import select

coords_photo_router = Router(name=__name__)


@coords_photo_router.message(Settings.coords)
async def coords_photo(msg: Message, state: FSMContext):
    try:
        if msg.location:
            session = await database.create_session()  # AsyncSession
            user = await session.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
            user = user.scalars().first()
            user.coord_x, user.coord_y = msg.location.latitude, msg.location.longitude
            async with Nominatim(user_agent='tg_bot',
                                 adapter_factory=AioHTTPAdapter) as geolocator:
                loc = await geolocator.reverse((user.coord_x, user.coord_y), exactly_one=True)
                address = loc.raw['address']
                user.city = address.get('city', 'none')
                try:
                    user.city = address['city']
                except Exception:
                    try:
                        user.city = address['state']
                    except Exception:
                        try:
                            user.city = address['region']
                        except Exception:
                            try:
                                user.city = address['country']
                            except Exception:
                                user.city = 'none'
            user.photos = ''
            await session.commit()
            await session.close()
            await msg.answer('<b>Пришлите свои фотографии (до 5, присылайте по одной фотографии за раз)</b>',
                             reply_markup=photos_kb())
            await state.set_state(Settings.photo)
        else:
            await msg.answer('<i>Укажите ваши координаты с помощью кнопки </i>', reply_markup=location_kb())
            await state.set_state(Settings.coords)
    except Exception as err:
        await msg.answer('<i>Пришлите свои координаты с помощью кнопки</i>')