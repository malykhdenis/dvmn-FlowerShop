from datetime import datetime, timedelta

import telebot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, Message
from environs import Env

from db_utils import get_reasons, get_requested_bouquets

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

    reasons = get_reasons()
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
        # clear info about previously filtered bouquets
        if 'found_bouquets' in data:
            del data['found_bouquets']
        if 'bouquet_index' in data:
            del data['bouquet_index']

    get_desired_price(message)


@bot.callback_query_handler(state=BotStates.select_reason,
                            func=lambda call: call.data != 'another_reason')
def proccess_reason(call: CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["username"] = call.from_user.username
        data['reason'] = call.data
    bot.edit_message_reply_markup(chat_id, message.message_id)

    get_desired_price(message)


def get_desired_price(message: Message) -> None:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        InlineKeyboardButton("~500₽", callback_data="750"),
        InlineKeyboardButton("~1000₽", callback_data="1250"),
        InlineKeyboardButton("~2000₽", callback_data="2250"),
        InlineKeyboardButton("Больше", callback_data="1000000"),
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

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        InlineKeyboardButton(
            'Заказать консультацию',
            callback_data="order_consultation"
        ),
    )

    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        if 'found_bouquets' not in data:
            bouquets = get_requested_bouquets(data['reason'], data['desired_price'])
            print(bouquets)
            data['found_bouquets'] = bouquets

        if 'bouquet_index' not in data:
            data['bouquet_index'] = 0
        else:
            data['bouquet_index'] = data['bouquet_index'] + 1

        try:
            if data['found_bouquets']:
                current_bouquet = data['found_bouquets'][data['bouquet_index']]
            else:
                current_bouquet = None
        except IndexError:
            # start showing bouquets from the beginning
            data['bouquet_index'] = 0
            current_bouquet = data['found_bouquets'][data['bouquet_index']]

    if not current_bouquet:
        bot.send_message(
            chat_id,
            'К сожалению, по вашему запросу ничего не найдено.\n\n'
            'Попробуйте уточнить свой запрос или закажите конcультацию '
            'флориста.\n\n'
            'Для нового заказа используйте команду /start.',
            reply_markup=inline_keyboard
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

    bot.send_message(
        chat_id,
        f'{current_bouquet["title"]}\n\n'
        'TODO: Описание букета.\n\n'
        f'Состав: {", ".join(flowers)}\n\n'
        f'Цена: {current_bouquet["price"]}\n\n'
        'Или хотите что-то ещё более уникальное? Подберите другой букет '
        'из нашей коллекции или закажите консультацию флориста.',
        reply_markup=inline_keyboard
    )

    # bot.send_photo(
    #     chat_id,
    #     "TODO_image_url",
    #     f'{current_bouquet["title"]}\n\n'
    #     'TODO: Описание букета.\n\n'
    #     f'Состав: {", ".join(flowers)}\n\n'
    #     f'Цена: {current_bouquet["price"]}\n\n'
    #     'Или хотите что-то ещё более уникальное? Подберите другой букет '
    #     'из нашей коллекции или закажите консультацию флориста.',
    #     reply_markup=inline_keyboard
    # )


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
        data["phone"] = message.text
        if data.get("order_consultation"):
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
        InlineKeyboardButton("Сегодня", callback_data="today"),
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
        case "today":
            delivery_date = current_daytime
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
        InlineKeyboardButton("9-13", callback_data="9-13"),
        InlineKeyboardButton("13-17", callback_data="13-17"),
        InlineKeyboardButton("17-21", callback_data="17-21")
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
        data["time"] = call.data

    bot.send_message(
        chat_id,
        'Ваш заказ принят. Наш менеджер скоро свяжется с вами '
        'для уточнения деталей.'
    )
    bot.set_state(message.from_user.id, BotStates.order_accepted)

    # TODO: make order processing


def consultation_ordered(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        'Консультация заказана. В скором времени с Вами свяжется наш флорист.'
    )
    bot.set_state(message.from_user.id, BotStates.consultation_ordered)


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    client = False  # TODO: get client from db

    bot.send_message(
        message.chat.id,
        'Закажите доставку праздничного букета, собранного специально для '
        'ваших любимых, родных и коллег.\n'
        'Наш букет со смыслом станет главным подарком на вашем празднике!'
    )
    if not client:
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
        return

    get_reason(message)


def main() -> None:
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()


if __name__ == '__main__':
    main()
