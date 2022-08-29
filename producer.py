# Purpose: Produce streaming sales and inventory activities to Kafka topics
# Author:  Gary A. Stafford
# Date: 2022-08-29
# Instructions: Modify the configuration.ini file to meet your requirements.

import configparser
import datetime
import json
import random
import time
from csv import reader

from kafka import KafkaProducer

config = configparser.ConfigParser()
config.read('configuration.ini')

# *** CONFIGURATION ***
bootstrap_servers = config['KAFKA']['bootstrap_servers']
topic_purchases = config['KAFKA']['topic_purchases']
topic_stockings = config['KAFKA']['topic_stockings']

min_sale_freq = int(config['SALES']['min_sale_freq'])
max_sale_freq = int(config['SALES']['max_sale_freq'])
number_of_sales = int(config['SALES']['number_of_sales'])
quantity_one_freq = int(config['SALES']['quantity_one_freq'])
member_freq = int(config['SALES']['member_freq'])
club_member_discount = float(config['SALES']['club_member_discount'])
add_supp_freq_group1 = int(config['SALES']['add_supp_freq_group1'])
add_supp_freq_group2 = int(config['SALES']['add_supp_freq_group2'])
supplements_cost = float(config['SALES']['supplements_cost'])

min_inventory = int(config['INVENTORY']['min_inventory'])
restock_amount = int(config['INVENTORY']['restock_amount'])

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
        self.total_purchase = self.quantity * (self.price + supplements_cost)
        if self.is_member:
            self.total_purchase = self.total_purchase * (1 - club_member_discount)
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
    def __init__(self, transaction_time, product_id, existing_level, stock_quantity, new_level):
        self.transaction_time = str(transaction_time)
        self.product_id = str(product_id)
        self.existing_level = int(existing_level)
        self.stock_quantity = int(stock_quantity)
        self.new_level = int(new_level)

    def __str__(self):
        return 'Stocking: time: {0}, product_id: {1}, existing_level: {2:.0f}, stock_quantity: {3:.0f}, ' \
               'new_level: {4:.0f}'.format(
            self.transaction_time,
            self.product_id,
            self.existing_level,
            self.stock_quantity,
            self.new_level
        )


def main():
    create_product_list()
    generate_sales()


# create a product and weighting lists from CSV data file
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


# generate synthetic sale transactions
def generate_sales():
    purchases = []
    for x in range(0, number_of_sales):
        range_min = product_weightings[0]
        range_max = product_weightings[-1]
        rnd_product_weight = closest_product_match(product_weightings, random.randint(range_min, range_max))
        quantity = random_quantity()
        for product in products:
            if product.range_weight == rnd_product_weight:
                add_supplement = random_add_supplements(product.product_id)
                supplement_price = supplements_cost if add_supplement else 0.00
                is_member = random_club_member()
                member_discount = club_member_discount if is_member else 0.00

                purchase = Purchase(
                    datetime.datetime.utcnow(),
                    product.product_id,
                    product.price,
                    random_quantity(),
                    is_member,
                    member_discount,
                    add_supplement,
                    supplement_price
                )
                purchases.append(purchase)
                publish_to_kafka(topic_purchases, purchase)
                product.inventory = product.inventory - quantity
                if product.inventory <= min_inventory:
                    restock_item(product.product_id)
                break
        time.sleep(random.randint(min_sale_freq, max_sale_freq))
    return purchases


# restock inventories
def restock_item(product_id):
    for product in products:
        if product.product_id == product_id:
            new_inventory = product.inventory + restock_amount
            stocking = Stocking(
                datetime.datetime.utcnow(),
                product.product_id,
                product.inventory,
                restock_amount,
                new_inventory
            )
            stockings.append(stocking)
            product.inventory = new_inventory  # update existing product item
            publish_to_kafka(topic_stockings, stocking)
            break


# publish a message to a kafka topic
def publish_to_kafka(topic, message):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    message = json.dumps(vars(message))
    producer.send(topic, value=message)
    print(message)


# find the closest match in weight range
# Credit: https://www.geeksforgeeks.org/python-find-closest-number-to-k-in-given-list/
def closest_product_match(lst, k):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - k))]


# purchase quantity (usually 1, max 2)
def random_quantity():
    rnd = random.randint(1, 10)
    if rnd <= quantity_one_freq:
        return 1
    return 2


# smoothie club membership? (usually False)
def random_club_member():
    rnd = random.randint(1, 10)
    if rnd <= member_freq:
        return True
    return False


# add supplements? (more frequently purchased for SF and SC products)
def random_add_supplements(product_id):
    rnd = random.randint(1, 10)
    if str(product_id).startswith('SF') or str(product_id).startswith('SC'):
        if rnd <= add_supp_freq_group1:
            return False
        return True
    if rnd <= add_supp_freq_group2:
        return True
    return False


if __name__ == '__main__':
    main()
