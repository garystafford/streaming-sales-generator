class Inventory:
    def __init__(
        self,
        event_time: str,
        product_id: str,
        existing_level: int,
        stock_quantity: int,
        new_level: int,
    ):
        self.event_time = str(event_time)
        self.product_id = str(product_id)
        self.existing_level = int(existing_level)
        self.stock_quantity = int(stock_quantity)
        self.new_level = int(new_level)

    def __str__(self):
        return (
            "Inventory: event_time: {0}, product_id: {1}, existing_level: {2:.0f}, stock_quantity: {3:.0f}, "
            "new_level: {4:.0f}".format(
                self.event_time,
                self.product_id,
                self.existing_level,
                self.stock_quantity,
                self.new_level,
            )
        )
