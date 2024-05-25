from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import token

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
