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
from models.inventory import Inventory

config = configparser.ConfigParser()
config.read("configuration/configuration.ini")

# *** CONFIGURATION ***
topic_products = config["KAFKA"]["topic_products"]
topic_purchases = config["KAFKA"]["topic_purchases"]
topic_inventories = config["KAFKA"]["topic_inventories"]

min_sale_freq = int(config["SALES"]["min_sale_freq"])
max_sale_freq = int(config["SALES"]["max_sale_freq"])
number_of_sales = int(config["SALES"]["number_of_sales"])
transaction_quantity_one_item_freq = int(
    config["SALES"]["transaction_quantity_one_item_freq"]
)
item_quantity_one_freq = int(config["SALES"]["item_quantity_one_freq"])
member_freq = int(config["SALES"]["member_freq"])
club_member_discount = float(config["SALES"]["club_member_discount"])
add_supp_freq_group1 = int(config["SALES"]["add_supp_freq_group1"])
add_supp_freq_group2 = int(config["SALES"]["add_supp_freq_group2"])
supplements_cost = float(config["SALES"]["supplements_cost"])

min_inventory = int(config["INVENTORY"]["min_inventory"])
restock_amount = int(config["INVENTORY"]["restock_amount"])

# *** VARIABLES ***
products = []
propensity_to_buy_range = []


def main():
    create_product_list()
    generate_sales()


# create products and propensity_to_buy lists from CSV data file
def create_product_list():
    with open("data/products.csv", "r") as csv_file:
        next(csv_file)  # skip header row
        csv_reader = reader(csv_file)
        csv_products = list(csv_reader)

    for p in csv_products:
        new_product = Product(
            str(datetime.utcnow()),
            p[0],
            p[1],
            p[2],
            p[3],
            p[4],
            p[5],
            p[6],
            to_bool(p[7]),
            to_bool(p[8]),
            to_bool(p[9]),
            to_bool(p[10]),
            p[14],
        )
        products.append(new_product)
        publish_to_kafka(topic_products, new_product)
        propensity_to_buy_range.append(int(p[14]))
    propensity_to_buy_range.sort()


# generate synthetic sale transactions
def generate_sales():
    # common to all transactions
    range_min = propensity_to_buy_range[0]
    range_max = propensity_to_buy_range[-1]
    for x in range(0, number_of_sales):
        # common for each transaction's line items
        transaction_time = str(datetime.utcnow())
        is_member = random_club_member()
        member_discount = club_member_discount if is_member else 0.00

        # reset values
        rnd_propensity_to_buy = -1
        previous_rnd_propensity_to_buy = -1

        for y in range(0, random_transaction_item_quantity()):
            # reduces but not eliminates risk of duplicate products in same transaction - TODO: improve this method
            if rnd_propensity_to_buy == previous_rnd_propensity_to_buy:
                rnd_propensity_to_buy = closest_product_match(
                    propensity_to_buy_range, random.randint(range_min, range_max)
                )
            previous_rnd_propensity_to_buy = rnd_propensity_to_buy
            quantity = random_quantity()
            for p in products:
                if p.propensity_to_buy == rnd_propensity_to_buy:
                    add_supplement = random_add_supplements(p.product_id)
                    supplement_price = supplements_cost if add_supplement else 0.00
                    new_purchase = Purchase(
                        transaction_time,
                        str(abs(hash(transaction_time))),
                        p.product_id,
                        p.price,
                        random_quantity(),
                        is_member,
                        member_discount,
                        add_supplement,
                        supplement_price,
                    )
                    publish_to_kafka(topic_purchases, new_purchase)
                    p.inventory_level = p.inventory_level - quantity
                    if p.inventory_level <= min_inventory:
                        restock_item(p.product_id)
                    break
        time.sleep(random.randint(min_sale_freq, max_sale_freq))


# restock inventories
def restock_item(product_id):
    for p in products:
        if p.product_id == product_id:
            new_level = p.inventory_level + restock_amount
            new_inventory = Inventory(
                str(datetime.utcnow()),
                p.product_id,
                p.inventory_level,
                restock_amount,
                new_level,
            )
            p.inventory_level = new_level  # update existing product item
            publish_to_kafka(topic_inventories, new_inventory)
            break


# serialize object to json and publish message to kafka topic
def publish_to_kafka(topic, message):
    configs = get_configs()

    producer = KafkaProducer(
        value_serializer=lambda v: json.dumps(vars(v)).encode("utf-8"),
        **configs,
    )
    producer.send(topic, value=message)
    print("Topic: {0}, Value: {1}".format(topic, message))


# convert uppercase boolean values from CSV file to Python
def to_bool(value):
    if type(value) == str and str(value).lower() == "true":
        return True
    return False


# find the closest match in propensity_to_buy_range range
# Credit: https://www.geeksforgeeks.org/python-find-closest-number-to-k-in-given-list/
def closest_product_match(lst, k):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - k))]


# individual item purchase quantity (usually 1, max 3)
def random_quantity():
    rnd = random.randint(1, 30)
    if rnd == 30:
        return 3
    if rnd <= item_quantity_one_freq:
        return 1
    return 2


# transaction items quantity (usually 1, max 3)
def random_transaction_item_quantity():
    rnd = random.randint(1, 20)
    if rnd >= 19:
        return 3
    if rnd <= transaction_quantity_one_item_freq:
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
    if str(product_id).startswith("SF") or str(product_id).startswith("SC"):
        if rnd <= add_supp_freq_group1:
            return True
        return False
    if rnd <= add_supp_freq_group2:
        return True
    return False


if __name__ == "__main__":
    main()
