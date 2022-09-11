class Product:
    def __init__(self, product_id: str, category: str, item: str, size: str, cogs: float, price: float, inventory: int,
                 contains_fruit: bool, contains_veggies: bool, contains_nuts: bool, contains_caffeine: bool,
                 range_weight: int):
        self.product_id = str(product_id)
        self.category = str(category)
        self.item = str(item)
        self.size = str(size)
        self.cogs = float(cogs)
        self.price = float(price)
        self.inventory = int(inventory)
        self.contains_fruit = bool(contains_fruit)
        self.contains_veggies = bool(contains_veggies)
        self.contains_nuts = bool(contains_nuts)
        self.contains_caffeine = bool(contains_caffeine)
        self.range_weight = int(range_weight)

    def __str__(self):
        return 'Product: product_id: {0}, category: {1}, item: {2}, size: {3}, cogs: ${4:.2f}, price: ${5:.2f}, ' \
               'inventory: {6:.0f}, contains_fruit: {7}, contains_veggies: {8}, contains_nuts: {9}, ' \
               'contains_caffeine: {10}'.format(
            self.product_id,
            self.category,
            self.item,
            self.size,
            self.cogs,
            self.price,
            self.inventory,
            self.contains_fruit,
            self.contains_veggies,
            self.contains_nuts,
            self.contains_caffeine
        )
