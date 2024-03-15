from datetime import datetime, timedelta

import telebot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, Message
from environs import Env
from requests.exceptions import HTTPError

from db_utils import get_reasons_from_db, get_requested_bouquets, \
    get_master_from_db, get_courier_from_db, create_client_in_db, \
    get_client_from_db, create_order_in_db

env = Env()
env.read_env()

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(
    token=env.str('TELEGRAM_BOT_TOKEN'),
    state_storage=state_storage
)


class BotStates(StatesGroup):
    start = State()
    approve_pd = State()
    select_reason = State()
    specify_reason = State()
    select_price = State()
    show_bouquet = State()
    show_another_bouquet = State()
    get_client_name = State()
    get_client_phone_number = State()
    get_client_address = State()
    get_delivery_date = State()
    get_delivery_time = State()
    order_accepted = State()
    consultation_ordered = State()


@bot.callback_query_handler(state=BotStates.approve_pd,
                            func=lambda call: call.data == 'yes')
def pd_approved(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    # bot.send_document(chat_id, open('agreement.pdf', 'rb'))
    bot.edit_message_reply_markup(chat_id, message.message_id)

    get_reason(message)


@bot.callback_query_handler(state=BotStates.approve_pd,
                            func=lambda call: call.data == 'no')
def pd_not_approved(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    button_approve_pd = InlineKeyboardButton(
        'Я согласен на обработку персональных данных',
        callback_data='yes'
    )
    inline_keyboard.add(button_approve_pd)

    bot.send_message(
        chat_id,
        'К сожалению, без согласия на обработку персональных данных '
        'вы не сможете заказать букет.',
        reply_markup=inline_keyboard
    )


def get_reason(message: Message) -> None:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)

    reasons = get_reasons_from_db()
    reason_buttons = [
        InlineKeyboardButton(
            reason['name'], callback_data=reason['name']
        ) for reason in reasons
    ]

    inline_keyboard.add(
        *reason_buttons,
        InlineKeyboardButton('Без повода', callback_data='no_reason'),
        InlineKeyboardButton('Другой повод', callback_data='another_reason'),
    )

    bot.send_message(
        message.chat.id,
        'К какому событию готовимся? Выберите один из вариантов '
        'или укажите свой.',
        reply_markup=inline_keyboard
    )
    bot.set_state(message.chat.id, BotStates.select_reason)


@bot.callback_query_handler(state=BotStates.select_reason,
                            func=lambda call: call.data == 'another_reason')
def get_custom_reason(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    bot.send_message(
        message.chat.id,
        'Расскажите нам, к какому событию вы бы хотели приобрести букет?',
    )
    bot.set_state(message.chat.id, BotStates.specify_reason)


@bot.message_handler(state=BotStates.specify_reason, func=lambda message: True)
def proccess_custom_reason(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["username"] = message.from_user.username
        data["reason"] = message.text

    get_desired_price(message)


@bot.callback_query_handler(state=BotStates.select_reason,
                            func=lambda call: call.data != 'another_reason')
def proccess_reason(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["username"] = call.from_user.username
        data['reason'] = call.data

    get_desired_price(message)


def get_desired_price(message: Message) -> None:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        InlineKeyboardButton("~500₽", callback_data="750"),
        InlineKeyboardButton("~1000₽", callback_data="1250"),
        InlineKeyboardButton("~2000₽", callback_data="2250"),
        InlineKeyboardButton("Больше", callback_data="overprice"),
        InlineKeyboardButton("Не важно", callback_data="0"),
    )

    bot.send_message(message.chat.id, 'На какую сумму рассчитываете?',
                     reply_markup=inline_keyboard)
    bot.set_state(message.chat.id, BotStates.select_price)


@bot.callback_query_handler(state=BotStates.select_price,
                            func=lambda call: True)
def process_desired_price(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data['desired_price'] = call.data
        # clear info about previously filtered bouquets if any
        if 'found_bouquets' in data:
            del data['found_bouquets']
        if 'bouquet_index' in data:
            del data['bouquet_index']
        if 'current_bouquet' in data:
            del data['current_bouquet']

    bot.set_state(message.chat.id, BotStates.show_bouquet)

    show_bouquet(call)


@bot.callback_query_handler(
    state=BotStates.show_bouquet,
    func=lambda call: call.data == "show_another_bouquet"
)
def show_bouquet(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    inline_keyboard_no_result = InlineKeyboardMarkup(row_width=1)
    inline_keyboard_no_result.add(
        InlineKeyboardButton(
            'Заказать консультацию',
            callback_data="order_consultation"
        ),
    )

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        if 'found_bouquets' not in data:
            data['found_bouquets'] = get_requested_bouquets(
                data['reason'], data['desired_price']
            )

        if 'bouquet_index' not in data:
            data['bouquet_index'] = 0
        else:
            data['bouquet_index'] += 1

        try:
            if data['found_bouquets']:
                current_bouquet = data['found_bouquets'][data['bouquet_index']]
            else:
                current_bouquet = None
        except IndexError:
            # start showing bouquets from the beginning
            data['bouquet_index'] = 0
            current_bouquet = data['found_bouquets'][data['bouquet_index']]
        data['current_bouquet'] = current_bouquet

    if not current_bouquet:
        bot.send_message(
            chat_id,
            'К сожалению, по вашему запросу ничего не найдено.\n\n'
            'Попробуйте уточнить свой запрос или закажите конcультацию '
            'флориста.\n\n'
            'Для нового заказа используйте команду /start.',
            reply_markup=inline_keyboard_no_result
        )
        return

    flowers = [flower['name'] for flower in current_bouquet['flowers']]

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        InlineKeyboardButton('Заказать этот букет', callback_data="order_bouquet"),
        InlineKeyboardButton(
            'Посмотреть следующий букет',
            callback_data="show_another_bouquet"
        ),
        InlineKeyboardButton(
            'Заказать консультацию',
            callback_data="order_consultation"
        ),
    )

    message_text = (
        f'{current_bouquet["title"]}\n\n'
        f'{current_bouquet["description"]}\n\n'
        f'Состав: {", ".join(flowers)}\n\n'
        f'Цена: {current_bouquet["price"]}₽\n\n'
        'Или хотите что-то ещё более уникальное? Подберите другой букет '
        'из нашей коллекции или закажите консультацию флориста.'
    )
    image_url = current_bouquet['photo']

    if image_url:
        bot.send_photo(
            chat_id,
            image_url,
            message_text,
            reply_markup=inline_keyboard
        )
        return

    bot.send_message(
        chat_id,
        message_text,
        reply_markup=inline_keyboard
    )


@bot.callback_query_handler(
    state=BotStates.show_bouquet,
    func=lambda call: call.data == "order_bouquet"
)
@bot.callback_query_handler(
    state=BotStates.show_bouquet,
    func=lambda call: call.data == "order_consultation"
)
def get_client_name(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        if call.data == "order_consultation":
            data["order_consultation"] = True

    bot.send_message(chat_id,
                     'Отлично. Скажите, как мы можем к Вам обращаться?')
    bot.set_state(chat_id, BotStates.get_client_name)


@bot.message_handler(state=BotStates.get_client_name,
                     func=lambda message: True)
def get_client_phone_number(message: Message) -> None:
    name = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["name"] = name

    bot.send_message(
        message.chat.id,
        f'Приятно познакомиться, {name}. Теперь введите ваш номер телефона.'
    )
    bot.set_state(message.from_user.id, BotStates.get_client_phone_number)


@bot.message_handler(state=BotStates.get_client_phone_number,
                     func=lambda message: True)
def proccess_client_phone_number(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["phone_number"] = message.text
        need_consultation = data.get("order_consultation")

    if need_consultation:
        consultation_ordered(message)
        return
    get_client_address(message)


def get_client_address(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        'Замечательно! Теперь введите адрес доставки.'
    )
    bot.set_state(message.from_user.id, BotStates.get_client_address)


@bot.message_handler(state=BotStates.get_client_address,
                     func=lambda message: True)
def get_delivery_date(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["address"] = message.text

    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        InlineKeyboardButton("Завтра", callback_data="tomorrow"),
        InlineKeyboardButton("Послезавтра",
                             callback_data="day_after_tomorrow"),
        InlineKeyboardButton("Другой день", callback_data="another_date")
    )

    bot.send_message(
        message.chat.id,
        'Уже почти всё. На какой день планируете доставку?',
        reply_markup=inline_keyboard
    )
    bot.set_state(message.from_user.id, BotStates.get_delivery_date)


@bot.callback_query_handler(state=BotStates.get_delivery_date,
                            func=lambda call: True)
def proccess_delivery_date(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    current_daytime = datetime.now()
    match call.data:
        case "tomorrow":
            delivery_date = current_daytime + timedelta(days=1)
        case "day_after_tomorrow":
            delivery_date = current_daytime + timedelta(days=2)
        case _:
            delivery_date = datetime(1970, 1, 1)

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["delivery_date"] = delivery_date

    get_delivery_time(message)


def get_delivery_time(message: Message) -> None:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        InlineKeyboardButton("9-13", callback_data="13"),
        InlineKeyboardButton("13-17", callback_data="17"),
        InlineKeyboardButton("17-21", callback_data="21")
    )
    bot.send_message(
        message.chat.id,
        'И последнее: в какое время вы можете принять курьера?',
        reply_markup=inline_keyboard
    )
    bot.set_state(message.chat.id, BotStates.get_delivery_time)


@bot.callback_query_handler(state=BotStates.get_delivery_time,
                            func=lambda call: True)
def order_accepted(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["delivery_time"] = call.data
        ic(data)
        client = {
            "username": data['username'],
            "address": data['address'],
            "phone_number": data['phone_number'],
            'name': data['name']
        }
        order = {
            'bouquet': data['current_bouquet'],
            'delivery_date': data['delivery_date'],
            'delivery_time': data['delivery_time']
        }
        bouquet = data['current_bouquet']

    try:
        client_id = create_client_in_db(
            client['username'],
            client['address'],
            client['phone_number']
        )['id']
    except HTTPError:
        client_id = get_client_from_db(client['username'])['id']

    delivery_datetime = datetime(
        order['delivery_date'].year,
        order['delivery_date'].month,
        order['delivery_date'].day,
        int(order['delivery_time'])
    )

    courier = get_courier_from_db()
    create_order_in_db(
        client_id,
        bouquet['id'],
        delivery_datetime,
        get_master_from_db()['id'],
        courier['id'],
        bouquet['price']  # TODO: price with delivery cost from courier model
    )

    courier_tg_id = courier['telegram_id']
    delivery_datetime_readable = delivery_datetime.strftime('%d/%m/%Y %H:%M')
    bot.send_message(
        courier_tg_id,
        'Поступил новый заказ.\n\n'
        f'Имя: {client["name"]}\n'
        f'Номер телефона: {client["phone_number"]}\n'
        f'Букет: {bouquet["title"]}\n'
        f'Цена: {bouquet["price"]}\n'
        f'Адрес доставки: {client["address"]}\n'
        f'Дата и время доставки: {delivery_datetime_readable}\n\n'
    )

    bot.send_message(
        chat_id,
        'Ваш заказ принят.\n\n'
        f'Букет: {bouquet["title"]}\n'
        f'Цена: {bouquet["price"]}\n'
        f'Адрес доставки: {client["address"]}\n'
        f'Дата и время доставки: {delivery_datetime_readable}\n\n'
        'Наш менеджер скоро свяжется с вами '
        'для уточнения деталей.'
    )
    bot.set_state(message.from_user.id, BotStates.order_accepted)


def consultation_ordered(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        client = {
            "name": data["name"],
            "phone_number": data["phone_number"],
            "reason": data["reason"],
            "desired_price": data['desired_price'],
        }

    bot.send_message(
        message.chat.id,
        'Консультация заказана. В скором времени с Вами свяжется наш флорист.'
    )

    master_id = get_master_from_db()['telegram_id']
    bot.send_message(
        master_id,
        'Новый заказ консультации:\n\n'
        f'Имя: {client["name"]}\n'
        f'Номер телефона: {client["phone_number"]}\n'
        f'Повод: {client["reason"]}\n'
        f'Желаемая цена: {client["desired_price"]}₽\n'
    )
    bot.set_state(message.from_user.id, BotStates.consultation_ordered)


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        'Закажите доставку праздничного букета, собранного специально для '
        'ваших любимых, родных и коллег.\n'
        'Наш букет со смыслом станет главным подарком на вашем празднике!'
    )

    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_yes = InlineKeyboardButton('Да', callback_data='yes')
    button_no = InlineKeyboardButton('Нет', callback_data='no')
    inline_keyboard.add(button_yes, button_no)

    bot.send_message(
        message.chat.id,
        'Для продолжения работы с ботом необходимо ваше согласие '
        'на обработку персональных данных.',
        reply_markup=inline_keyboard)
    bot.set_state(message.from_user.id,
                  BotStates.approve_pd, message.chat.id)


def main() -> None:
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()


if __name__ == '__main__':
    main()
