import datetime
from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from states import ExchangeState
from coingecko import get_usdt_uah_price, get_usdt_rub_price
from config import ADMIN_ID


async def process_currency(callback_query: types.CallbackQuery, state: FSMContext):
    currency = callback_query.data.split("_")[1]
    await state.update_data(currency=currency)

    if currency == "Гривны":
        button = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Skrill ➡️ Приват24",
                        callback_data="exchange_Skrill_Приват24",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Paxum ➡️ Приват24", callback_data="exchange_Paxum_Приват24"
                    )
                ],
            ],
        )
    else:
        button = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Skrill ➡️ Тинькофф",
                        callback_data="exchange_Skrill_Тинькофф",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Skrill ➡️ Сбер", callback_data="exchange_Skrill_Сбер"
                    )
                ],
            ],
        )

    await callback_query.message.answer(
        "Выберите пару для обмена:", reply_markup=button
    )
    await state.set_state(ExchangeState.choice)


async def process_choice(callback_query: types.CallbackQuery, state: FSMContext):
    exchange_pair = callback_query.data.split("_")[1]
    await state.update_data(exchange_pair=exchange_pair)

    await callback_query.message.answer(
        "Пожалуйста, введите сумму вашего обмена в USDT."
    )
    await state.set_state(ExchangeState.amount)


async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount < 5:
            await message.answer("Минимальная сумма обмена 5 USDT.")
            return

        await state.update_data(amount=amount)

        data = await state.get_data()
        currency = data["currency"]
        if currency == "Гривны":
            rate = get_usdt_uah_price()
        else:
            rate = get_usdt_rub_price()

        await message.answer(
            f"Вы получите {amount * rate} {currency.lower()} на ваш счет.\n"
            f"Пожалуйста, укажите ваш банковский счет."
        )
        await state.set_state(ExchangeState.wallet)
    except ValueError:
        await message.answer("Пожалуйста, введите корректные данные.")


async def process_wallet(message: types.Message, state: FSMContext):
    await state.update_data(wallet=message.text)

    button = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Подтверждаю оплату", callback_data="confirm_payment"
                )
            ]
        ],
    )

    data = await state.get_data()
    amount = data["amount"]
    wallet = data["wallet"]
    currency = data["currency"]
    if currency == "Гривны":
        rate = get_usdt_uah_price()
    else:
        rate = get_usdt_rub_price()

    await message.answer(
        f"Вы обмениваете {amount} USDT на {amount * rate} {currency.lower()}.\n"
        f"Ваш счет: {wallet}\n\n"
        f"Мы ожидаем от вас оплаты на USDT кошелек в размере {amount} USDT по реквизитам: UQDc8TkqJUgtHMC_8oiNszXvNjbUVNm5oIBS1mmm3voAapx9",  # надо изменить на твой кошелек, куда будешь принимать USDT
        reply_markup=button,
    )
    await state.set_state(ExchangeState.confirmation)


async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "confirm_payment":
        data = await state.get_data()
        amount = data["amount"]
        wallet = data["wallet"]
        currency = data["currency"]
        if currency == "Гривны":
            rate = get_usdt_uah_price()
        else:
            rate = get_usdt_rub_price()

        await callback_query.message.answer(
            f"Ваша заявка была создана {datetime.datetime.now()}. Обмен происходит в течение нескольких минут.\n"
            "Спасибо за оказанное доверие.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[]),
        )
        await callback_query.bot.send_message(
            ADMIN_ID,
            f"Сумма обмена: {amount} USDT\n"
            f"Сумма к получению: {amount * rate} {currency.lower()}\n"
            f"На счет: {wallet}\n\n"
            f"Время создания заявки: {datetime.datetime.now()}\n"
            f"User ID: {callback_query.from_user.id}",
        )
        await state.clear()
    else:
        await callback_query.message.answer(
            "Пожалуйста, подтвердите оплату, нажав на кнопку."
        )


# async def view_requests(message: types.Message):
#     if message.from_user.id == int(ADMIN_ID):
#         await message.answer("Заявки: ...")  # Заглушка для списка заявок
#     else:
#         await message.answer("У вас нет прав для выполнения этой команды.")


async def reply_to_user(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        try:
            args = message.text.split(" ", 2)
            user_id = int(args[1])
            reply_message = args[2]
            await message.bot.send_message(user_id, reply_message)
            await message.answer("Сообщение отправлено пользователю.")
        except (IndexError, ValueError):
            await message.answer(
                "Неправильный формат команды. Используйте: /reply <user_id> <message>"
            )
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")


async def close_request(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        try:
            args = message.text.split(" ", 1)
            user_id = int(args[1])
            await message.bot.send_message(
                user_id, "Ваша заявка была закрыта администратором."
            )
            await message.answer("Заявка закрыта.")
        except (IndexError, ValueError):
            await message.answer(
                "Неправильный формат команды. Используйте: /close <user_id>"
            )
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")


def register_exchange_handlers(dp: Dispatcher):
    dp.callback_query.register(process_currency, ExchangeState.currency)
    dp.callback_query.register(process_choice, ExchangeState.choice)
    dp.message.register(process_amount, ExchangeState.amount)
    dp.message.register(process_wallet, ExchangeState.wallet)
    dp.callback_query.register(process_confirmation, ExchangeState.confirmation)
    # dp.message.register(view_requests, Command(commands=["view_requests"]))
    dp.message.register(reply_to_user, Command(commands=["reply"]))
    dp.message.register(close_request, Command(commands=["close"]))
