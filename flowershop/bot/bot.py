import logging
from datetime import datetime, timedelta

import telebot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, Message
from environs import Env
from requests.exceptions import HTTPError

from bot_utils.db_utils import get_reasons_from_db, get_requested_bouquets, \
    get_master_from_db, get_courier_from_db, create_client_in_db, \
    get_client_from_db, create_order_in_db, create_consultation_in_db
from bot_utils import bot_messages as msg
from bot_utils import bot_buttons as btn

env = Env()
env.read_env()

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(
    token=env.str('TELEGRAM_BOT_TOKEN'),
    state_storage=state_storage
)
telebot.logger.setLevel(logging.INFO)


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

    bot.send_document(chat_id, open('agreement.pdf', 'rb'))
    bot.edit_message_reply_markup(chat_id, message.message_id)

    get_reason(message)


@bot.callback_query_handler(state=BotStates.approve_pd,
                            func=lambda call: call.data == 'no')
def pd_not_approved(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        InlineKeyboardButton(btn.PD_YES, callback_data='yes')
    )

    bot.send_message(
        chat_id,
        msg.PD_RESTRICT,
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
        InlineKeyboardButton(btn.NO_REASON, callback_data='no_reason'),
        InlineKeyboardButton(btn.ANOTHER_REASON,
                             callback_data='another_reason'),
    )

    bot.send_message(
        message.chat.id,
        msg.GET_REASON,
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
        msg.GET_CUSTOM_REASON,
    )
    bot.set_state(message.chat.id, BotStates.specify_reason)


@bot.message_handler(state=BotStates.specify_reason, func=lambda message: True)
def proccess_custom_reason(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['username'] = message.from_user.username
        data['reason'] = message.text
        data['reason_id'] = None

    get_desired_price(message)


@bot.callback_query_handler(state=BotStates.select_reason,
                            func=lambda call: call.data != 'another_reason')
def proccess_reason(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data['username'] = call.from_user.username
        data['reason'] = call.data
        data['reason_id'] = None

    get_desired_price(message)


def get_desired_price(message: Message) -> None:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        InlineKeyboardButton('~500₽', callback_data='500'),
        InlineKeyboardButton('~1000₽', callback_data='1000'),
        InlineKeyboardButton('~2000₽', callback_data='2000'),
        InlineKeyboardButton('Больше', callback_data='2001'),
        InlineKeyboardButton('Не важно', callback_data='0'),
    )

    bot.send_message(message.chat.id, msg.GET_DESIRED_PRICE,
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
    func=lambda call: call.data == 'show_another_bouquet'
)
@bot.callback_query_handler(
    state=BotStates.consultation_ordered,
    func=lambda call: call.data == 'show_all_bouquets'
)
def show_bouquet(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    inline_keyboard_no_result = InlineKeyboardMarkup(row_width=1)
    inline_keyboard_no_result.add(
        InlineKeyboardButton(
            btn.ORDER_CONSULTATION,
            callback_data='order_consultation'
        ),
    )

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        if call.data == 'show_all_bouquets':
            bot.set_state(message.chat.id, BotStates.show_bouquet)
            # update data to show all bouquets
            data['reason'] = 'no_reason'
            data['desired_price'] = '0'
            data['order_consultation'] = False
            data['found_bouquets'] = get_requested_bouquets(
                data['reason'], data['desired_price']
            )

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
            msg.BOUQUETS_NOT_FOUND,
            reply_markup=inline_keyboard_no_result
        )
        return

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        InlineKeyboardButton(btn.ORDER_BOUQUET,
                             callback_data='order_bouquet'),
        InlineKeyboardButton(
            btn.SHOW_ANOTHER_BOUQUET,
            callback_data='show_another_bouquet'
        ),
        InlineKeyboardButton(
            btn.ORDER_CONSULTATION,
            callback_data='order_consultation'
        ),
    )

    message_text = msg.generate_bouquet_info(current_bouquet)
    image_url = current_bouquet['photo']
    if image_url:
        bot.send_photo(chat_id, image_url)

    bot.send_message(
        chat_id,
        message_text,
        reply_markup=inline_keyboard,
        parse_mode='markdown'
    )


@bot.callback_query_handler(
    state=BotStates.show_bouquet,
    func=lambda call: call.data == 'order_bouquet'
)
@bot.callback_query_handler(
    state=BotStates.show_bouquet,
    func=lambda call: call.data == 'order_consultation'
)
def get_client_name(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        if call.data == 'order_consultation':
            data['order_consultation'] = True

    bot.send_message(chat_id, msg.GET_CLIENT_NAME)
    bot.set_state(chat_id, BotStates.get_client_name)


@bot.message_handler(state=BotStates.get_client_name,
                     func=lambda message: True)
def get_client_phone_number(message: Message) -> None:
    name = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = name

    bot.send_message(
        message.chat.id,
        ' '.join([msg.generate_user_greeting(name), msg.GET_CLIENT_PHONE])
    )
    bot.set_state(message.from_user.id, BotStates.get_client_phone_number)


@bot.message_handler(state=BotStates.get_client_phone_number,
                     func=lambda message: True)
def proccess_client_phone_number(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['phone_number'] = message.text
        need_consultation = data.get('order_consultation')

    if need_consultation:
        consultation_ordered(message)
        return
    get_client_address(message)


def get_client_address(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        msg.GET_CLIENT_ADDRESS
    )
    bot.set_state(message.from_user.id, BotStates.get_client_address)


@bot.message_handler(state=BotStates.get_client_address,
                     func=lambda message: True)
def get_delivery_date(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['address'] = message.text

    current_day = datetime.now().date()
    avaliable_dates = [
        InlineKeyboardButton(
            (current_day + timedelta(days=day)).strftime('%d.%m.%y'),
            callback_data=(
                current_day + timedelta(days=day)
            ).strftime('%d.%m.%y')
        ) for day in range(1, 5)
    ]

    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        *avaliable_dates
    )

    bot.send_message(
        message.chat.id,
        msg.GET_DELIVERY_DATE,
        reply_markup=inline_keyboard
    )
    bot.set_state(message.from_user.id, BotStates.get_delivery_date)


@bot.callback_query_handler(state=BotStates.get_delivery_date,
                            func=lambda call: True)
def proccess_delivery_date(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data['delivery_date'] = datetime.strptime(call.data, '%d.%m.%y')

    get_delivery_time(message)


def get_delivery_time(message: Message) -> None:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        InlineKeyboardButton('9-13', callback_data='13'),
        InlineKeyboardButton('13-17', callback_data='17'),
        InlineKeyboardButton('17-21', callback_data='21')
    )
    bot.send_message(
        message.chat.id,
        msg.GET_DELIVERY_TIME,
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
        data['delivery_time'] = call.data
        client = {
            'username': data['username'],
            'address': data['address'],
            'phone_number': data['phone_number'],
            'name': data['name']
        }
        order = {
            'bouquet': data['current_bouquet'],
            'delivery_date': data['delivery_date'],
            'delivery_time': data['delivery_time']
        }
        bouquet = data['current_bouquet']

    delivery_datetime = datetime(
        order['delivery_date'].year,
        order['delivery_date'].month,
        order['delivery_date'].day,
        int(order['delivery_time'])
    )

    try:
        client_id = create_client_in_db(
            client['username'],
            client['address'],
            client['phone_number']
        )['id']
    except HTTPError:
        client_id = get_client_from_db(client['username'])['id']

    courier = get_courier_from_db()
    price_with_delivery = courier['orders_count'] + bouquet['price']
    new_order = create_order_in_db(
        client_id,
        bouquet['id'],
        delivery_datetime,
        get_master_from_db()['id'],
        courier['id'],
        price_with_delivery
    )

    courier_tg_id = courier['telegram_id']
    order_info = msg.generate_order_info(
        new_order['id'],
        client["name"],
        client["phone_number"],
        bouquet["title"],
        price_with_delivery,
        client["address"],
        delivery_datetime
    )
    bot.send_message(
        courier_tg_id,
        ''.join([
            msg.NEW_ORDER_ACCEPTED,
            order_info
        ])
    )

    bot.send_message(
        chat_id,
        ''.join([
            msg.YOUR_ORDER_ACCEPTED,
            order_info,
            msg.MANAGER_CONTACT
        ])
    )
    bot.set_state(message.from_user.id, BotStates.order_accepted)


def consultation_ordered(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['order_consultation'] = False
        client = {
            'username': data['username'],
            'name': data['name'],
            'phone_number': data['phone_number'],
            'reason': data['reason'],
            'reason_id': data['reason_id'],
            'desired_price': data['desired_price'],
        }

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        InlineKeyboardButton(btn.SHOW_ALL_BOUQUETS,
                             callback_data='show_all_bouquets')
    )

    try:
        client_id = create_client_in_db(
            client['username'],
            phone_number=client['phone_number']
        )['id']
    except HTTPError:
        client_id = get_client_from_db(client['username'])['id']

    master = get_master_from_db()
    master_id = master['id']
    master_tg_id = master['telegram_id']

    # TODO: Get reason by it's ID
    create_consultation_in_db(
        client_id,
        master_id,
        desired_price=client['desired_price']
    )

    bot.send_message(
        master_tg_id,
        msg.generate_message_for_master(client)
    )

    bot.send_message(
        message.chat.id,
        msg.CONSULTATION_ORDERED,
        reply_markup=inline_keyboard
    )
    bot.set_state(message.from_user.id, BotStates.consultation_ordered)


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        msg.WELCOME
    )

    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_yes = InlineKeyboardButton(btn.YES, callback_data='yes')
    button_no = InlineKeyboardButton(btn.NO, callback_data='no')
    inline_keyboard.add(button_yes, button_no)

    bot.send_message(
        message.chat.id,
        msg.PD_AGREEMENT,
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
