def calculate_stock_status(stock: int) -> str:
    if stock <= 0:
        return "out_of_stock"
    if stock <= 5:
        return "low_stock"
    return "in_stock"
