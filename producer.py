# Purpose: Produces products, streaming sales transactions, and restocking activities to Kafka topics
# Author:  Gary A. Stafford
# Date: 2022-08-29
# Instructions: Modify the configuration.ini file to meet your requirements.

import configparser
import json
import random
import time
from csv import reader
from datetime import datetime

from kafka import KafkaProducer

from config.kafka import get_configs
from models.product import Product
from models.purchase import Purchase
from models.stocking import Stocking

config = configparser.ConfigParser()
config.read('configuration/configuration.ini')

# *** CONFIGURATION ***
topic_products = config['KAFKA']['topic_products']
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


def main():
    create_product_list()
    generate_sales()


# create products and weightings lists from CSV data file
def create_product_list():
    with open('data/products.csv', 'r') as csv_file:
        next(csv_file)  # skip header row
        csv_reader = reader(csv_file)
        csv_products = list(csv_reader)

    for p in csv_products:
        new_product = Product(p[0], p[1], p[2], p[3], p[4], p[5], p[6], to_bool(p[7]), to_bool(p[8]), to_bool(p[9]),
                              to_bool(p[10]), p[14])
        products.append(new_product)
        publish_to_kafka(topic_products, new_product)
        product_weightings.append(int(p[14]))
    product_weightings.sort()


# generate synthetic sale transactions
def generate_sales():
    for x in range(0, number_of_sales):
        range_min = product_weightings[0]
        range_max = product_weightings[-1]
        rnd_product_weight = closest_product_match(product_weightings, random.randint(range_min, range_max))
        quantity = random_quantity()
        for p in products:
            if p.range_weight == rnd_product_weight:
                add_supplement = random_add_supplements(p.product_id)
                supplement_price = supplements_cost if add_supplement else 0.00
                is_member = random_club_member()
                member_discount = club_member_discount if is_member else 0.00

                new_purchase = Purchase(
                    str(datetime.utcnow()),
                    p.product_id,
                    p.price,
                    random_quantity(),
                    is_member,
                    member_discount,
                    add_supplement,
                    supplement_price
                )
                publish_to_kafka(topic_purchases, new_purchase)
                p.inventory = p.inventory - quantity
                if p.inventory <= min_inventory:
                    restock_item(p.product_id)
                break
        time.sleep(random.randint(min_sale_freq, max_sale_freq))


# restock inventories
def restock_item(product_id):
    for p in products:
        if p.product_id == product_id:
            new_inventory = p.inventory + restock_amount
            new_stocking = Stocking(
                str(datetime.utcnow()),
                p.product_id,
                p.inventory,
                restock_amount,
                new_inventory
            )
            p.inventory = new_inventory  # update existing product item
            publish_to_kafka(topic_stockings, new_stocking)
            break


# serialize object to json and publish message to kafka topic
def publish_to_kafka(topic, message):
    configs = get_configs()

    producer = KafkaProducer(
        value_serializer=lambda v: json.dumps(vars(v)).encode('utf-8'),
        **configs
    )
    producer.send(topic, value=message)
    print('Topic: {0}, Value: {1}'.format(topic, message))


# convert uppercase boolean values from CSV file to Python
def to_bool(value):
    if type(value) == str and str(value).lower() == 'true':
        return True
    return False


# find the closest match in weight range
# Credit: https://www.geeksforgeeks.org/python-find-closest-number-to-k-in-given-list/
def closest_product_match(lst, k):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - k))]


# purchase quantity (usually 1, max 3)
def random_quantity():
    rnd = random.randint(1, 30)
    if rnd == 30:
        return 3
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
            return True
        return False
    if rnd <= add_supp_freq_group2:
        return True
    return False


if __name__ == '__main__':
    main()
