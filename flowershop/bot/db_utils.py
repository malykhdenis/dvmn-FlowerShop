import requests as rq


def get_from_db(db_url: str, payload: dict = None) -> list:
    response = rq.get(db_url, params=payload)
    response.raise_for_status()
    print(response.url)

    return response.json()


def get_reasons_from_db() -> list:
    url = "http://127.0.0.1:8000/api/v1/reasons"
    return get_from_db(url)


def get_requested_bouquets(reason: str = None, price: str = None) -> list:
    print(reason, price)
    url = "http://127.0.0.1:8000/api/v1/bouquets"

    payload = {}

    if reason != 'no_reason':
        payload['search'] = reason

    if price == 'overprice':
        payload['overprice'] = True
    elif price != '0':
        payload['price__lte'] = price

    return get_from_db(url, payload)


def create_order_in_db():
    pass


def get_courier_id_from_db():
    pass
