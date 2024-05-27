from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from .buttons import (langs_kb_buttons, who_kb_buttons, find_who_kb_buttons, photos_kb_button, location_kb_button, \
                     text_of_anketa_button, main_menu_kb_button, show_profile_kb_button, photos_del_or_not_kb_button, \
                     like_or_not_kb_button, main_menu_kb_button_premium, premium_types_kb_buttons,
                     like_or_not_kb_button_premium,
                     premium_settings_kb_button)
from data.change_profile_user import ChangeProfileCallback
from commands_inline_user import PremiumInline, PremiumSettings


def langs_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for i in langs_kb_buttons:
        builder.button(text=i)
    return builder.as_markup(resize_keyboard=True)


def who_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for i in who_kb_buttons:
        builder.button(text=i)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def location_kb():
    builder = ReplyKeyboardBuilder()
    for i in location_kb_button:
        builder.button(text=i, request_location=True)
    return builder.as_markup(resize_keyboard=True)


def find_who_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for i in find_who_kb_buttons:
        builder.button(text=i)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def photos_kb():
    builder = ReplyKeyboardBuilder()
    for i in photos_kb_button:
        builder.button(text=i)
    return builder.as_markup(resize_keyboard=True)


def text_of_anketa_kb():
    builder = ReplyKeyboardBuilder()
    for i in text_of_anketa_button:
        builder.button(text=i)
    return builder.as_markup(resize_keyboard=True)


def main_menu_anketa_kb():
    builder = InlineKeyboardBuilder()
    for text, callback in main_menu_kb_button:
        builder.button(text=text, callback_data=callback)
    builder.adjust(1)
    return builder.as_markup()


def main_menu_anketa_kb_premium():
    builder = InlineKeyboardBuilder()
    for text, callback in main_menu_kb_button_premium:
        builder.button(text=text, callback_data=callback)
    builder.adjust(1)
    return builder.as_markup()


def change_parameters_kb():
    builder = InlineKeyboardBuilder()
    for text, callback in show_profile_kb_button:
        builder.button(text=text, callback_data=ChangeProfileCallback(part=callback).pack())
    builder.adjust(2)
    return builder.as_markup()


def yes_or_no_photos_kb():
    builder = ReplyKeyboardBuilder()
    for text in photos_del_or_not_kb_button:
        builder.button(text=text)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def like_or_not_kb():
    builder = ReplyKeyboardBuilder()
    for text in like_or_not_kb_button:
        builder.button(text=text)
    # builder.adjust()
    return builder.as_markup(resize_keyboard=True)


def like_or_not_premium_kb():
    builder = ReplyKeyboardBuilder()
    for text in like_or_not_kb_button_premium:
        builder.button(text=text)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


def premium_types_kb():
    builder = InlineKeyboardBuilder()
    for text, callback in premium_types_kb_buttons:
        builder.button(text=text, callback_data=PremiumInline(days=callback).pack())
    builder.adjust(1)
    return builder.as_markup()

def premium_settings_kb():
    builder = InlineKeyboardBuilder()
    for text, callback in premium_settings_kb_button:
        builder.button(text=text, callback_data=PremiumSettings(settings=callback).pack())
    builder.adjust(1)
    return builder.as_markup()

