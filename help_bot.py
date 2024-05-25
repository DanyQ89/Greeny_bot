import sqlite3

import asyncio
from aiogram import Router, Dispatcher, Bot, F, filters
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram import types
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.methods import edit_message_text, edit_message_reply_markup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from io import BytesIO
import logging
from config import token
from data.database import create_session
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# conn = sqlite3.connect('./db/my_database.sqlite')
# cursor = conn.cursor()
router = Router()
class SA(StatesGroup):
    media = State()

def help_kb():
    buider = ReplyKeyboardBuilder()
    buider.add()
@router.message(Command('start'))
async def send_media(msg: Message, state: FSMContext):
    # await msg.answer('@' + msg.from_user.username)
    session =  create_session()
    user = session
    await msg.answer('meow')
    await state.set_state(SA.media)

@router.message(SA.media)
async def second_func(msg: Message, state: FSMContext):
    text = msg.text
    await msg.answer(str(len(text)), text)


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())