import pytest
import requests
import os
import random
import uuid


@pytest.fixture(scope="session")
def http_client():
    client = requests.Session()
    client.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )
    return client

@pytest.fixture(scope="session")
def api_endpoint() -> str:
    return os.getenv("SERVICE_BASE_URL", "https://qa-internship.avito.com")
  
def validate_uuid_format(candidate: str) -> bool:
    try:
        uuid.UUID(candidate)
        return True
    except (ValueError, TypeError):
        return False


def parse_identifier_from_message(message: str) -> str:
    segments = message.split(" - ", maxsplit=1)
    if len(segments) != 2:
        raise ValueError(f"Неожиданный формат сообщения: {message!r}")
    return segments[1].strip()


@pytest.fixture
def vendor_identifier() -> int:
    return random.randint(111111, 999999)


@pytest.fixture
def listing_entry(http_client, api_endpoint, vendor_identifier):
    request_body = {
        "sellerId": vendor_identifier,
        "name": "Тестовый товар",
        "price": 1500,
        "statistics": {
            "likes": 5,
            "viewCount": 25,
            "contacts": 8,
        },
    }

    response = http_client.post(f"{api_endpoint}/api/1/item", json=request_body)

    assert response.status_code == 200, f"Ожидался код 200 при создании, получен {response.status_code}"
    response_data = response.json()
    assert "status" in response_data, "В ответе создания отсутствует поле 'status'"
    assert "Сохранили объявление -" in response_data["status"], "Статус не содержит ожидаемой формулировки"

    entry_identifier = parse_identifier_from_message(response_data["status"])
    assert validate_uuid_format(entry_identifier), f"Идентификатор не соответствует формату UUID: {entry_identifier}"

    return {
        "id": entry_identifier,
        "sellerId": vendor_identifier,
        "requestData": request_body,
    }
