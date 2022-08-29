# Yet Another Streaming Data Generator (YASDG)

## TL;DR

1. Run the command `docker stack deploy kafka --compose-file docker-compose.yml` to create local instance of Kafka
2. Run the command `python3 ./producer.py` to start generating streaming data to Kafka
3. Run the command `python3 ./consumer.py` in a separate terminal window to view results

## Background

Everytime you want to explore a new streaming technology or create a customer demonstration, first you must find a good
source of streaming data, or create something new each time. Ideally, the data is complex enough to perform multiple
analyses and visualize different aspects. Additionally, it should have some predictable patterns but is not totally
random or results if an even distribution over time.

This configurable data generator streams drink products, synthetic sales transactions, and product inventory activities
to Apache Kafka. It is designed for demonstrating streaming data analytics tools, such as Apache Spark Structured
Streaming, Apache Flink, Apache Pinot, Databricks, and Amazon Kinesis Data Analytics.

## Highlights

* All configuration in a separate `configuration.ini` file
* Nothing is completely random - variables are weighted and can be adjusted in `.ini` file
* Over 25 smoothie drink products: descriptions, inventories, product weightings
* Writes initial product list to an Apache Kafka topic (topic 1)
* Generates streaming drink purchases, with time, item, quantity, price, total price, etc.
* Writes smoothie purchases to an Apache Kafka topic (topic 2)
* Club membership discounts semi-randomly applied to smoothie purchases
* Add-on supplements semi-randomly applied to smoothie purchases
* Restocks low product inventories based on a minimum value
* Writes restocking activities to a second Apache Kafka topic: time, old inventory, new inventory, etc. (topic 3)

## Product Samples

Products roughly based on Tropical Smoothie menu
from [Fast Food Menu Prices](https://www.fastfoodmenuprices.com/tropical-smoothie-prices/). Last four columns, with `_`,
are used
to generate artificial product category and product weightings, which determine how frequently the products are
purchased in the simulation.

```text
ID,Category,Item,Size,Price,Inventory,ContainsFruit,ContainsVeggies,ContainsNuts,ContainsCaffeine,_CatWeight,_ItemWeight,_TotalWeight,_RangeWeight
CS01,Classic Smoothies,Sunrise Sunset,24 oz.,4.99,75,1,0,0,0,3,2,6,6
CS02,Classic Smoothies,Kiwi Quencher,24 oz.,4.99,75,1,0,0,0,3,5,15,21
SF07,Superfoods Smoothies,Detox Island Green,24 oz.,5.99,50,1,1,0,0,2,1,2,136
SC04,Supercharged Smoothies,Lean Machine,24 oz.,5.99,35,0,1,1,1,3,4,12,184
IS04,Indulgent Smoothies,Mocha Madness,24 oz.,5.49,60,0,0,1,1,4,2,8,242
```

## Product Samples

```json
[
    {
        "product_id": "CS01",
        "category": "Classic Smoothies",
        "item": "Sunrise Sunset",
        "size": "24 oz.",
        "price": 4.99,
        "inventory": 75,
        "contains_fruit": true,
        "contains_veggies": false,
        "contains_nuts": false,
        "contains_caffeine": false,
        "range_weight": 6
    },
    {
        "product_id": "SF01",
        "category": "Superfoods Smoothies",
        "item": "Island Green",
        "size": "24 oz.",
        "price": 5.99,
        "inventory": 50,
        "contains_fruit": true,
        "contains_veggies": true,
        "contains_nuts": false,
        "contains_caffeine": false,
        "range_weight": 108
    },
    {
        "product_id": "SC02",
        "category": "Supercharged Smoothies",
        "item": "Peanut Paradise",
        "size": "24 oz.",
        "price": 5.99,
        "inventory": 35,
        "contains_fruit": false,
        "contains_veggies": false,
        "contains_nuts": false,
        "contains_caffeine": false,
        "range_weight": 160
    },
    {
        "product_id": "SC03",
        "category": "Supercharged Smoothies",
        "item": "Health Nut",
        "size": "24 oz.",
        "price": 5.99,
        "inventory": 35,
        "contains_fruit": false,
        "contains_veggies": false,
        "contains_nuts": true,
        "contains_caffeine": false,
        "range_weight": 172
    },
    {
        "product_id": "IS04",
        "category": "Indulgent Smoothies",
        "item": "Mocha Madness",
        "size": "24 oz.",
        "price": 5.49,
        "inventory": 60,
        "contains_fruit": false,
        "contains_veggies": false,
        "contains_nuts": true,
        "contains_caffeine": true,
        "range_weight": 242
    }
]
```

## Transaction Samples

```json
[
    {
        "transaction_time": "2022-08-29 12:39:06.178496",
        "product_id": "CS08",
        "price": 4.99,
        "quantity": 1,
        "is_member": false,
        "member_discount": 0.0,
        "add_supplements": false,
        "supplement_price": 0.0,
        "total_purchase": 6.98
    },
    {
        "transaction_time": "2022-08-29 12:39:09.523024",
        "product_id": "SC02",
        "price": 5.99,
        "quantity": 2,
        "is_member": false,
        "member_discount": 0.0,
        "add_supplements": true,
        "supplement_price": 1.99,
        "total_purchase": 15.96
    },
    {
        "transaction_time": "2022-08-29 12:39:12.973486",
        "product_id": "CS09",
        "price": 4.99,
        "quantity": 1,
        "is_member": false,
        "member_discount": 0.0,
        "add_supplements": false,
        "supplement_price": 0.0,
        "total_purchase": 6.98
    },
    {
        "transaction_time": "2022-08-29 12:39:17.233186",
        "product_id": "SC01",
        "price": 5.99,
        "quantity": 1,
        "is_member": true,
        "member_discount": 0.1,
        "add_supplements": false,
        "supplement_price": 0.0,
        "total_purchase": 7.18
    }
]
```

## Restocking Activity Samples

```json
[
    {
        "transaction_time": "2022-08-29 15:09:23.007874",
        "product_id": "SC05",
        "existing_level": 9,
        "stock_quantity": 15,
        "new_level": 24
    },
    {
        "transaction_time": "2022-08-29 15:12:30.415329",
        "product_id": "SC03",
        "existing_level": 10,
        "stock_quantity": 15,
        "new_level": 25
    },
    {
        "transaction_time": "2022-08-29 15:19:38.139400",
        "product_id": "SC01",
        "existing_level": 10,
        "stock_quantity": 15,
        "new_level": 25
    },
    {
        "transaction_time": "2022-08-29 15:34:35.392350",
        "product_id": "SC04",
        "existing_level": 9,
        "stock_quantity": 15,
        "new_level": 24
    },
    {
        "transaction_time": "2022-08-29 15:48:55.183778",
        "product_id": "IS01",
        "existing_level": 10,
        "stock_quantity": 15,
        "new_level": 25
    }
]
```

## Commands

See [bitnami/kafka](https://hub.docker.com/r/bitnami/kafka) on Docker Hub for more information about running Kafka
locally using Docker.

```shell
docker stack deploy kafka --compose-file docker-compose.yml

docker container ls
docker exec -it <docker_container_name> bash
```

To run the application:

```shell
python3 ./producer.py
python3 ./consumer.py
```

From within the Kafka container:

```shell
export BOOTSTRAP_SERVERS="localhost:9092"
export TOPIC_PRODUCTS="smoothie.products"
export TOPIC_PURCHASES="smoothie.purchases"
export TOPIC_STOCKINGS="smoothie.stockings"

# delete topics
kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --delete --topic $TOPIC_PRODUCTS
kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --delete --topic $TOPIC_PURCHASES
kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --delete --topic $TOPIC_STOCKINGS

# read topics from beginning
kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS \
  --topic $TOPIC_PRODUCTS --from-beginning
kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS \
  --topic $TOPIC_PURCHASES --from-beginning
kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS \
  --topic $TOPIC_STOCKINGS --from-beginning
```

---
_The contents of this repository represent my viewpoints and not of my past or current employers, including Amazon Web
Services (AWS). All third-party libraries, modules, plugins, and SDKs are the property of their respective owners. The
author(s) assumes no responsibility or liability for any errors or omissions in the content of this site. The
information contained in this site is provided on an "as is" basis with no guarantees of completeness, accuracy,
usefulness or timeliness._

