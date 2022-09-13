class Purchase:
    def __init__(
        self,
        transaction_time: str,
        transaction_id: str,
        product_id: str,
        price: float,
        quantity: int,
        is_member: bool,
        member_discount: float,
        add_supplements: bool,
        supplement_price: float,
    ):
        self.transaction_time = str(transaction_time)
        self.transaction_id = str(transaction_id)
        self.product_id = str(product_id)
        self.price = float(price)
        self.quantity = int(quantity)
        self.is_member = bool(is_member)
        self.member_discount = float(member_discount)
        self.add_supplements = bool(add_supplements)
        self.supplement_price = float(supplement_price)
        self.total_purchase = self.quantity * (self.price + supplement_price)
        self.total_purchase = self.total_purchase * (1 - member_discount)
        self.total_purchase = round(self.total_purchase, 2)

    def __str__(self):
        return (
            "Purchase: transaction_time: {0}, transaction_id: {1}, product_id: {2}, quantity: {3:.0f}, "
            "price: ${4:.2f}, add_supplements: {5}, supplement_price: ${6:.2f}, is_member: {7}, "
            "member_discount: {8:.0%}, total: ${9:.2f}".format(
                self.transaction_time,
                self.transaction_id,
                self.product_id,
                self.quantity,
                self.price,
                self.add_supplements,
                self.supplement_price,
                self.is_member,
                self.member_discount,
                self.total_purchase,
            )
        )
