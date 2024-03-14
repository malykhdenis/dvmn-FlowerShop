import requests as rq


def get_from_db(db_url: str, payload: dict = None) -> list:
    response = rq.get(db_url, params=payload)
    response.raise_for_status()
    print(response.url)

    return response.json()


def get_reasons() -> list:
    url = "http://127.0.0.1:8000/api/v1/reasons"
    return get_from_db(url)


def get_requested_bouquets(reason: str, price: str) -> list:
    print(reason, price)
    url = "http://127.0.0.1:8000/api/v1/bouquets"

    payload = {}

    if reason != 'no_reason':
        payload['search'] = reason

    if price != '0':
        payload['price__lte'] = price

    return get_from_db(url, payload)


def get_client(username: str) -> None:
    url = "http://127.0.0.1:8000/api/v1/clients"
