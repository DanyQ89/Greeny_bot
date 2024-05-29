import schedule
import datetime
from data import database
import asyncio

from data.user_form import User
from sqlalchemy import select


async def job():
    now = datetime.datetime.now()
    current_time = str(now.strftime("%Y-%m-%d %H:%M"))
    db_session = await database.create_session()
    users = await db_session.execute(select(User).filter_by(end_premium=current_time))
    users = users.scalars().all()
    array_of_users = [user.id for user in users]
    for tg_id in array_of_users:
        user = await db_session.execute(select(User).filter_by(user_id=str(tg_id)))
        user = user.scalars().first()
        user.premium = False
        user.premium_like = 0
        user.premium_back = 0
    await db_session.close()


async def recovery():
    db_session = await database.create_session()
    users = await db_session.execute(select(User).filter_by(premium=True))
    users = users.scalars().all()
    array_of_users = [user.id for user in users]
    for tg_id in array_of_users:
        user = await db_session.execute(select(User).filter_by(user_id=str(tg_id)))
        user = user.scalars().first()
        user.premium_like = 1
        user.premium_back = 3
    await db_session.close()

import datetime

now = datetime.datetime.now()
future_date = now + datetime.timedelta(days=30)
print(type(future_date))

print(f"In 30 days, the date will be: {future_date.strftime('%Y-%m-%d %H:%M')}")