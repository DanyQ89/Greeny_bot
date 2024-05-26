from aiogram import Router

from .commands import router as commands_router
from .premium_commands import premium_router

router = Router(name=__name__)

router.include_routers(commands_router, premium_router)