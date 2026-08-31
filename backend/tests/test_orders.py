def test_order_total():
    from app.services.order_service import calculate_order_total
    assert calculate_order_total([
        {"price": 100, "quantity": 2},
        {"price": 50, "quantity": 1},
    ]) == 250
