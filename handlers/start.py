from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import ExchangeState


async def send_welcome(message: types.Message, state: FSMContext):
    button = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Гривны", callback_data="currency_Гривен"
                )
            ],
            [types.InlineKeyboardButton(text="Рубли", callback_data="currency_Рублей")],
        ],
    )

    await message.answer(
        "👨‍💻 Привет! Это обменник Crypto Adult\n\n"
        "💵 В данном Боте вы можете вывести свои средства с таких площадок, как:\n\n"
        "🟢 Skrill\n\n"
        "🟢 Paxum\n\n"
        "🔴 PayPal\n\n"
        "🔴 IBAN\n\n"
        "🔴 Hyperwallet\n\n"
        "🔴 WebMoney\n\n"
        "🔴 SEPA\n\n"
        "💻 Техническая поддержка: @CryptoAdultSupport\n\n"
        "💬 Чат Обменника: @Crypto_Adult_Chat\n\n"
        "👇 Для начала обмена, выберите нужную валюту👇",
        reply_markup=button,
    )
    await state.set_state(ExchangeState.currency)


def register_start_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command(commands=["start"]))
