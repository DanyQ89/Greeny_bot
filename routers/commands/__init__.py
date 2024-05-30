__all__ = ("router", )

from aiogram import Router

from .base_commands import router as base_commands_router
from .choose_language import lang_name_router
from .enter_name import name_age_router
from .enter_age import age_height_router
from .enter_height import height_coords_router
from .enter_coords import coords_photo_router
from .enter_photos import photo_text_router
from .enter_description import text_who_router
from .find_who import who_find_who_router
from .show_profile import show_profile_router
from .change_parameters import change_parameters_router
from .find_profiles import find_profiles_router
from .buy_premium import premium_router
from utils.help_functions import help_functions_router
from .check_likes import check_likes_router
from .set_inactive_user import disable_router

router = Router()

router.include_routers(base_commands_router, lang_name_router, name_age_router, age_height_router,
                       height_coords_router, coords_photo_router, photo_text_router, text_who_router,
                       who_find_who_router, show_profile_router, change_parameters_router, find_profiles_router,
                       premium_router, help_functions_router, check_likes_router, disable_router)