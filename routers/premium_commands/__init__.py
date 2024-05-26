__all__ = ("premium_router", )

from aiogram import Router

from p_enter_height import premium_height_router
from p_enter_age import premium_age_height_router

premium_router = Router()

premium_router.include_routers(premium_height_router, premium_age_height_router)

