from aiogram import Dispatcher
from .start import register_start_handlers
from .exchange import register_exchange_handlers


def register_handlers(dp: Dispatcher):
    register_start_handlers(dp)
    register_exchange_handlers(dp)
