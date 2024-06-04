import datetime
import asyncio
from data import database

from data.user_form import User
from sqlalchemy import select, and_
from main import bot


async def job():
    now = datetime.date.today()

    db_session = await database.create_session()
    users = await db_session.execute(select(User).filter(and_(User.premium == 1, User.end_premium <= now)))
    users = users.scalars().all()
    array_of_users = [user.id for user in users]
    for db_id in array_of_users:
        user = await db_session.execute(select(User).filter_by(id=db_id))
        user = user.scalars().first()
        user.premium = 0
        user.premium_like = 0
        user.premium_back = 0
        user.minAge = user.age - 2
        user.maxAge = user.age + 2
        user.minHeight = 100
        user.maxHeight = 250
        user.end_premium = None
        await bot.send_message(chat_id=int(user.user_id), text='<b>Премиум подписка закончилась</b>')
        await db_session.commit()
    await db_session.close()


async def recovery():
    db_session = await database.create_session()
    users = await db_session.execute(select(User).filter_by(premium=1))
    users = users.scalars().all()
    array_of_users = [user.id for user in users]
    for tg_id in array_of_users:
        user = await db_session.execute(select(User).filter_by(id=tg_id))
        user = user.scalars().first()
        user.premium_like = max(1, user.premium_like)
        user.premium_back = max(3, user.premium_back)
        await db_session.commit()
    await db_session.close()


async def check():
    while True:
        await job()
        await recovery()
        await asyncio.sleep(60 * 60 * 24)
