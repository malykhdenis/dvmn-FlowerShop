from datetime import datetime


WELCOME = (
    'Закажите доставку праздничного букета, собранного специально для '
    'ваших любимых, родных и коллег.\n'
    'Наш букет со смыслом станет главным подарком на вашем празднике!'
)

PD_AGREEMENT = (
    'Для продолжения работы с ботом необходимо ваше согласие '
    'на обработку персональных данных.'
)

PD_RESTRICT = (
    'К сожалению, без согласия на обработку персональных данных '
    'вы не сможете заказать букет.'
)

GET_REASON = (
    'К какому событию готовимся? Выберите один из вариантов '
    'или укажите свой.'
)
GET_CUSTOM_REASON = (
    'Расскажите нам, к какому событию вы бы хотели приобрести букет?'
)

GET_DESIRED_PRICE = 'На какую сумму рассчитываете?'

BOUQUETS_NOT_FOUND = (
    'К сожалению, по вашему запросу ничего не найдено.\n\n'
    'Попробуйте уточнить свой запрос или закажите конcультацию '
    'флориста.\n\n'
    'Для нового заказа используйте команду /start.',
)

ORDER_CONSULTATION = (
    '*Или хотите что-то ещё более уникальное? Подберите другой букет '
    'из нашей коллекции или закажите консультацию флориста.*'
)

GET_CLIENT_NAME = 'Отлично. Скажите, как мы можем к Вам обращаться?'
GET_CLIENT_PHONE = 'Теперь введите ваш номер телефона.'
GET_CLIENT_ADDRESS = 'Замечательно! Теперь введите адрес доставки.'
GET_DELIVERY_DATE = 'Уже почти всё. На какой день планируете доставку?'
GET_DELIVERY_TIME = 'И последнее: в какое время вы можете принять курьера?'

CONSULTATION_ORDERED = (
    'Консультация заказана. '
    'В скором времени с Вами свяжется наш флорист.\n\n'
    'А пока можете посмотреть нашу коллекцию букетов.'
)

NEW_ORDER_ACCEPTED = 'Поступил новый заказ.\n\n'
YOUR_ORDER_ACCEPTED = 'Ваш заказ принят.\n\n'
MANAGER_CONTACT = (
    'Наш менеджер скоро свяжется с вами '
    'для уточнения деталей.'
)


def generate_bouquet_info(bouquet: dict) -> str:
    '''
    Generates bouquet description according to given bouquet instanse.
    '''
    flowers = [flower['name'] for flower in bouquet['flowers']]

    bouquet_description = (
        f'{bouquet["title"]}\n\n'
        f'{bouquet["description"]}\n\n'
        f'Состав: {", ".join(flowers)}\n\n'
        f'Цена: {bouquet["price"]}₽\n\n'
    )

    return bouquet_description + ORDER_CONSULTATION


def generate_user_greeting(name: str) -> str:
    return f'Приятно познакомиться, {name}.'


def generate_message_for_master(client: dict) -> str:
    '''
    Generates message for master that contains all necessary
    information about client.
    '''
    message = (
        'Новый заказ консультации:\n\n'
        f'Имя: {client["name"]}\n'
        f'Номер телефона: {client["phone_number"]}\n'
        f'Повод: {client["reason"]}\n'
        f'Желаемая цена: {client["desired_price"]}₽\n'
    )

    return message


def generate_order_info(
        name: str,
        phone_number: str,
        bouquet_title: str,
        price: int,
        address: str,
        delivery_datetime: datetime
) -> str:
    '''
    Generates information about client's order.
    '''
    delivery_datetime_readable = delivery_datetime.strftime('%d/%m/%Y %H:%M')

    order_info = (
        f'Имя: {name}\n'
        f'Номер телефона: {phone_number}\n'
        f'Букет: {bouquet_title}\n'
        f'Цена с доставкой: {price}\n'
        f'Адрес доставки: {address}\n'
        f'Дата и время доставки: {delivery_datetime_readable}\n\n'
    )

    return order_info
