from aiogram import Router, F, types
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram.fsm.context import FSMContext
from data import database
from sqlalchemy import select
from data.user_form import User
import logging
import datetime
from bot import bot
from utils.help_functions import show_user_profile
from utils.keyboards import premium_types_kb, main_menu_anketa_kb_premium, main_menu_anketa_kb
from commands_inline_user import PremiumInline
from data.database import create_session

premium_router = Router(name=__name__)


@premium_router.callback_query(F.data == 'get_premium')
async def choose_premium(query: CallbackQuery, state: FSMContext):
    await state.clear()
    session = await create_session()
    user = await session.execute(select(User).filter_by(user_id=str(query.message.chat.id)))
    user = user.scalars().first()
    if user.premium:
        await query.message.edit_text(f'<b>Вам доступен Premium до {user.end_premium}\n'
                                      'Выберите длительность подписки:</b>', reply_markup=premium_types_kb())
    else:
        await query.message.edit_text('<b>Выберите длительность подписки:</b>', reply_markup=premium_types_kb())


@premium_router.callback_query(PremiumInline.filter())
async def premium(query: CallbackQuery, state: FSMContext):
    await state.clear()
    number = query.data.split(':')[1]
    if number == 'come_home':
        session = await database.create_session()
        user = await session.execute(select(User).filter_by(user_id=str(query.message.chat.id)))
        user = user.scalars().first()
        if user.premium:
            await query.message.edit_text('<b>Выберите действие:</b>', reply_markup=main_menu_anketa_kb_premium())
        else:
            await query.message.edit_text('<b>Выберите действие:</b>', reply_markup=main_menu_anketa_kb())
        await state.clear()
    else:
        if number == '30':
            amount = 299 * 100
        elif number == '60':
            amount = 599 * 100
        elif number == '90':
            amount = 1299 * 100
        else:
            amount = 1999 * 100

        await query.message.answer_invoice(
            title='✨Greeny premium✨',
            description=f'🟢Premium-Подписка на {number} дней🟢',
            payload='premium_invoice_payload',
            provider_token='1744374395:TEST:2927d276fa3aae2fcd47',
            currency='RUB',
            prices=[LabeledPrice(label=f'✨{number} дней Greeny Premium✨', amount=amount)]
        )


@premium_router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@premium_router.message(lambda message: message.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(msg: Message, state: FSMContext):
    payment_info = msg.successful_payment
    logging.info(f"Successful payment: {payment_info}")
    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(user_id=str(msg.from_user.id)))
    user = user.scalars().first()
    user.premium = True
    if not user.end_premium:
        date = datetime.date.today()
    else:
        date = user.end_premium

    to_delta = payment_info.total_amount
    if to_delta == 29900:
        days = 30
    elif to_delta == 59900:
        days = 60
    elif to_delta == 129900:
        days = 90
    else:
        days = 0
    delta = datetime.timedelta(days=days)

    date += delta
    user.end_premium = date

    await msg.answer(f"<b>Поздравляем с активацией Premium-подписки до {user.end_premium}!</b>")
    await sess.commit()
    await sess.close()
    await show_user_profile(msg, state)
