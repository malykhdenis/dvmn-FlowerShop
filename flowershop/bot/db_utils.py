import requests as rq


def get_from_db(db_url: str) -> list:
    response = rq.get(db_url)
    response.raise_for_status()

    return response.json()


def get_requested_bouquets(reason: str, price: int) -> list:
    main_url = "http:127.0.0.1:8000/api/v1/bouquets/"

    payload = {}

    if reason.isdigit():
        payload['reason']