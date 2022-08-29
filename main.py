import datetime
import random
import time
import json
from kafka import KafkaProducer
from csv import reader

# *** CONSTANTS ***
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_PURCHASE = 'smoothie.purchases'
TOPIC_STOCKING = 'smoothie.stockings'

MIN_SALE_FREQ = 120  # minimum sales frequency in seconds
MAX_SALE_FREQ = 300  # maximum sales frequency in seconds
NUMBER_OF_SALES = 100  # number of transactions to generate

CLUB_MEMBER_DISCOUNT = .10  # % discount for smoothie club members
SUPPLEMENTS_COST = 1.99  # cost of adding supplements to smoothie

IS_MEMBER = 3  # chance of being member on scale of 1 to 10?
QUANTITY_ONE = 8  # chance of quantity being 1 vs. 2 on scale of 1 to 10?
ADD_SUPP_SF_SC = 5  # chance of adding a supplement to SF or SC smoothies on scale of 1 to 10?
ADD_SUPP_CS_IS = 2  # chance of adding a supplement to CS or IS smoothies on scale of 1 to 10?

MIN_INVENTORY = 10  # minimum inventory level
RESTOCK_AMOUNT = 15  # restocking amount

# *** VARIABLES ***
products = []
product_weightings = []
stockings = []


class Product:
    def __init__(self, product_id, category, item, size, price, inventory, contains_fruit,
                 contains_veggies, contains_nuts, contains_caffeine, range_weight):
        self.product_id = str(product_id)
        self.category = str(category)
        self.item = str(item)
        self.size = str(size)
        self.price = float(price)
        self.inventory = int(inventory)
        self.contains_fruit = bool(contains_fruit)
        self.contains_veggies = bool(contains_veggies)
        self.contains_nuts = bool(contains_nuts)
        self.contains_caffeine = bool(contains_caffeine)
        self.range_weight = int(range_weight)

    def __str__(self):
        return 'Product: product_id: {0}, category: {1}, item: {2}, size: {3}, price: ${4:.2f}, inventory: {5:.0f}, ' \
               'contains_fruit: {6}, contains_veggies: {7}, contains_nuts: {8}, contains_caffeine: {9}'.format(
            self.product_id,
            self.category,
            self.item,
            self.size,
            self.price,
            self.inventory,
            self.contains_fruit,
            self.contains_veggies,
            self.contains_nuts,
            self.contains_caffeine
        )


class Purchase:
    def __init__(self, transaction_time, product_id, price, quantity, is_member,
                 member_discount, add_supplements, supplement_price):
        self.transaction_time = str(transaction_time)
        self.product_id = str(product_id)
        self.price = float(price)
        self.quantity = int(quantity)
        self.is_member = bool(is_member)
        self.member_discount = float(member_discount)
        self.add_supplements = bool(add_supplements)
        self.supplement_price = float(supplement_price)
        self.total_purchase = self.quantity * (self.price + SUPPLEMENTS_COST)
        if self.is_member:
            self.total_purchase = self.total_purchase * (1 - CLUB_MEMBER_DISCOUNT)
        self.total_purchase = round(self.total_purchase, 2)

    def __str__(self):
        return 'Purchase: time: {0}, product_id: {1}, quantity: {2:.0f}, price: ${3:.2f}, ' \
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


class Stocking:
    def __init__(self, transaction_time, product_id, existing_level, new_level):
        self.transaction_time = str(transaction_time)
        self.product_id = str(product_id)
        self.existing_level = int(existing_level)
        self.new_level = int(new_level)

    def __str__(self):
        return 'Stocking: time: {0}, product_id: {1}, existing_level: {2}, new_level: {3}'.format(
            self.transaction_time,
            self.product_id,
            self.existing_level,
            self.new_level
        )


def main():
    create_product_list()

    purchases = generate_sales()
    for purchase in purchases:
        print(purchase)

    for product in products:
        print(product)


# product list from csv file
def create_product_list():
    with open('products.csv', 'r') as csv_file:
        next(csv_file)  # skip header row
        csv_reader = reader(csv_file)
        csv_products = list(csv_reader)

    for p in csv_products:
        product = Product(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[13])
        products.append(product)
        product_weightings.append(int(p[13]))
    product_weightings.sort()


# generate sales
def generate_sales():
    purchases = []
    for x in range(0, NUMBER_OF_SALES):
        range_min = product_weightings[0]
        range_max = product_weightings[-1]
        rnd_product_weight = closest_product_match(product_weightings, random.randint(range_min, range_max))
        quantity = random_quantity()
        for product in products:
            if product.range_weight == rnd_product_weight:
                add_supplement = random_add_supplements(product.product_id)
                supplement_price = SUPPLEMENTS_COST if add_supplement else 0.00
                is_member = random_club_member()
                member_discount = CLUB_MEMBER_DISCOUNT if is_member else 0.00
                purchase = Purchase(
                    datetime.datetime.utcnow(),
                    product.product_id,
                    product.price,
                    random_quantity(),
                    random_club_member(),
                    member_discount,
                    add_supplement,
                    supplement_price
                )
                product.inventory = product.inventory - quantity
                purchases.append(purchase)
                print(purchase)
                publish_to_kafka(TOPIC_PURCHASE, purchase)
                if product.inventory <= MIN_INVENTORY:
                    restock_item(product.product_id)
                break
        time.sleep(random.randint(MIN_SALE_FREQ, MAX_SALE_FREQ))
    return purchases


# restock inventories
def restock_item(product_id):
    for product in products:
        if product.product_id == product_id:
            new_inventory = product.inventory + RESTOCK_AMOUNT
            stocking = Stocking(
                datetime.datetime.utcnow(),
                product.product_id,
                product.inventory,
                new_inventory
            )
            stockings.append(stocking)
            print(stocking)
            product.inventory = new_inventory
            publish_to_kafka(TOPIC_STOCKING, stocking)
            break


# publish messages to kafka
def publish_to_kafka(topic, message):
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    message = json.dumps(vars(message))
    print(message)
    producer.send(topic, value=message)


# find the closest match in weight range
# Credit: https://www.geeksforgeeks.org/python-find-closest-number-to-k-in-given-list/
def closest_product_match(lst, k):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - k))]


# purchase quantity (usually 1, max 2)
def random_quantity():
    rnd = random.randint(1, 10)
    if rnd <= QUANTITY_ONE:
        return 1
    return 2


# smoothie club membership? (usually False)
def random_club_member():
    rnd = random.randint(1, 10)
    if rnd <= IS_MEMBER:
        return True
    return False


# add supplements? (more frequently purchased for SF and SC products)
def random_add_supplements(product_id):
    rnd = random.randint(1, 10)
    if str(product_id).startswith('SF') or str(product_id).startswith('SC'):
        if rnd <= ADD_SUPP_SF_SC:
            return False
        return True
    if rnd <= ADD_SUPP_CS_IS:
        return True
    return False


if __name__ == '__main__':
    main()
