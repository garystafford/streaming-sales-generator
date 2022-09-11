class Purchase:
    def __init__(self, transaction_time: str, product_id: str, price: float, quantity: int, is_member: bool,
                 member_discount: float, add_supplements: bool, supplement_price: float):
        self.transaction_time = str(transaction_time)
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
        return 'Purchase: transaction_time: {0}, product_id: {1}, quantity: {2:.0f}, price: ${3:.2f}, ' \
               'add_supplements: {4}, supplement_price: ${5:.2f}, is_member: {6}, ' \
               'member_discount: {7:.0%}, total: ${8:.2f}'.format(
            self.transaction_time,
            self.product_id,
            self.quantity,
            self.price,
            self.add_supplements,
            self.supplement_price,
            self.is_member,
            self.member_discount,
            self.total_purchase
        )
