from aiogram import Dispatcher
import logging
import asyncio
import os
from bot import bot
from routers import router
from data.database import init_models
from routers.premium_commands import check_time_of_premium

logging.basicConfig(level=logging.INFO)


async def main():
    await init_models()
    dp = Dispatcher()
    dp.include_router(router)
    await asyncio.gather(
        check_time_of_premium.check(),
        dp.start_polling(bot),
    )


if __name__ == '__main__':
    os.environ['DEBUG'] = 'True'
    asyncio.run(main())
