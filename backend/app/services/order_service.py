def calculate_order_total(items: list[dict]) -> float:
    return sum(float(item["price"]) * int(item["quantity"]) for item in items)
