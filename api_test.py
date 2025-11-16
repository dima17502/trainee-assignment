def test_retrieve_item_statistics(session, base_url, created_item):
    target_item_identifier = created_item["id"]
    
    api_response = session.get(f"{base_url}/api/1/statistic/{target_item_identifier}")

    expected_status = 200
    assert api_response.status_code == expected_status

    statistics_data = api_response.json()

    if type(statistics_data) == list:
        minimum_expected_count = 1
        assert len(statistics_data) >= minimum_expected_count, "Статистика должна содержать минимум одну запись"
        statistics_data = statistics_data[0]

    required_metric_fields = ("likes", "viewCount", "contacts")
    for metric_name in required_metric_fields:
        assert metric_name in statistics_data, f"Отсутствует обязательный показатель: {metric_name}"
        assert isinstance(statistics_data[metric_name], int), f"Показатель {metric_name} должен быть целым числом"


def test_fetch_seller_listings(session, base_url, created_item):
    vendor_identifier = created_item["sellerId"]
    
    response_object = session.get(f"{base_url}/api/1/{vendor_identifier}/item")

    success_code = 200
    assert response_object.status_code == success_code

    parsed_content = response_object.json()
    assert isinstance(parsed_content, list)
    
    minimum_items_count = 1
    assert len(parsed_content) >= minimum_items_count

    existing_item_ids = {listing["id"] for listing in parsed_content}
    assert created_item["id"] in existing_item_ids


def test_verify_item_creation(session, base_url, seller_id):
    request_payload = {
        "sellerId": seller_id,
        "name": "Пробное объявление",
        "price": 1000,
        "statistics": {
            "likes": 10,
            "viewCount": 20,
            "contacts": 30,
        },
    }

    api_result = session.post(f"{base_url}/api/1/item", json=request_payload)

    expected_http_code = 200
    assert api_result.status_code == expected_http_code
    
    response_body = api_result.json()
    assert "status" in response_body
    expected_status_prefix = "Сохранили объявление -"
    assert expected_status_prefix in response_body["status"]


def test_validate_item_retrieval(session, base_url, created_item):
    specific_item_id = created_item["id"]

    http_response = session.get(f"{base_url}/api/1/item/{specific_item_id}")

    assert http_response.status_code == 200

    response_data = http_response.json()
    assert isinstance(response_data, list)
    
    minimum_expected_results = 1
    assert len(response_data) >= minimum_expected_results

    first_item = response_data[0]
    assert first_item["id"] == specific_item_id
    assert first_item["sellerId"] == created_item["sellerId"]
    assert first_item["name"] == created_item["payload"]["name"]
    assert first_item["price"] == created_item["payload"]["price"]
    assert "statistics" in first_item
    assert type(first_item["statistics"]) == dict
