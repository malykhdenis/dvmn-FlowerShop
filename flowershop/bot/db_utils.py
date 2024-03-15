from datetime import datetime

import requests as rq


def get_from_db(db_url: str, payload: dict = None) -> list:
    response = rq.get(db_url, params=payload)
    response.raise_for_status()

    return response.json()


def post_to_db(db_url: str, data: dict = None) -> dict:
    response = rq.post(db_url, data=data)
    response.raise_for_status()

    return response.json()


def get_reasons_from_db() -> list:
    url = "http://127.0.0.1:8000/api/v1/reasons"
    return get_from_db(url)


def get_requested_bouquets(reason: str = None, price: str = None) -> list:
    url = "http://127.0.0.1:8000/api/v1/bouquets"

    payload = {}

    if reason != 'no_reason':
        payload['search'] = reason

    if price == 'overprice':
        payload['overprice'] = True
    elif price != '0':
        payload['price__lte'] = price

    return get_from_db(url, payload)


def create_client_in_db(
    username: str,
    address: str = None,
    phone_number: str = None
) -> dict:
    url = "http://127.0.0.1:8000/api/v1/clients/"

    data = {
        "username": username,
        "address": address,
        "phone_number": phone_number,
    }

    return post_to_db(url, data)


def get_client_from_db(username: str) -> dict:
    url = "http://127.0.0.1:8000/api/v1/clients/"

    payload = {
        "search": username
    }

    return get_from_db(url, payload)


def get_courier_from_db() -> str:
    url = 'http://127.0.0.1:8000/api/v1/courier/1'
    return get_from_db(url)


def get_master_from_db() -> str:
    url = 'http://127.0.0.1:8000/api/v1/master/1'
    return get_from_db(url)


def create_order_in_db(
        client_id: str,
        bouquet_id: str,
        date_time: datetime,
        master_id: str,
        courier_id: str,
        total_price: str
) -> dict:
    url = 'http://127.0.0.1:8000/api/v1/orders/'
    data = {
        'client_id': client_id,
        'bouquet_id': bouquet_id,
        'date_time': date_time,
        'master_id': master_id,
        'courier_id': courier_id,
        'total_price': total_price,
    }

    return post_to_db(url, data)
