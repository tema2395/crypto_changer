from aiogram.fsm.state import StatesGroup, State

class ExchangeState(StatesGroup):
    choice = State()
    currency = State()  
    amount = State()
    wallet = State()
    confirmation = State()
