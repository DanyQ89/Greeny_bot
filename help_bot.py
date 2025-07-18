import sqlite3

import asyncio
from aiogram import Router, Dispatcher, Bot, filters
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram import types
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.methods import edit_message_text, edit_message_reply_markup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from utils.keyboards import link_and_check_kb
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from io import BytesIO
import logging
from config import token
from data.database import create_session
import requests
import json
import uuid
from routers.commands.buy_premium import create_payment
import aiohttp


bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

router = Router()

class F(StatesGroup):
    photo = State()
@router.message(Command('start'))
async def start(msg: Message, state: FSMContext):
    url, id = create_payment(10000.00, str(msg.chat.id))
    await msg.answer(f"Ваша ссылка: {url}")

@router.message(F.photo)
async def send_media(msg: Message, state: FSMContext):
    photo = msg.photo[-1].file_id
    print(photo)
    photo = await msg.bot.download(photo)
    # print(photo.read())



async def main():
    dp = Dispatcher()
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())