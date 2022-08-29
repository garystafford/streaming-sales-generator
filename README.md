# Yet Another Streaming Data Generator (YASDG)

## TL;DR

1. Run the command `docker-compose up -d` to create local instance of Kafka
2. Run the command `python3 ./producer.py` to generate streaming data
3. Run the command `python3 ./consumer.py` in a separate terminal window to view results

## Background

Everytime you want to explore a new streaming technology or create a customer demonstration, first you must find a good
source of streaming data, or create something new each time. Ideally, the data is complex enough to perform multiple
analyses and visualize different aspects. Additionally, it should have some predictable patterns but is not totally
random or results if an even distribution over time.

This configurable data generator streams synthetic drink sales transactions and product inventory activities to Apache
Kafka for demonstrating streaming data analytics tools, such as Apache Spark Structured Streaming, Apache Flink, Apache
Pinot, Databricks, Amazon Kinesis Data Analytics.

## Highlights

* All configuration in the `configuration.ini` file
* Nothing is completely random - variables are weighted and can be adjusted in `.ini` file
* Over 25 smoothie drink products: descriptions, inventories, product weightings
* Generates streaming drink purchases with: time, item, quantity, price, total price, etc.
* Writes smoothie purchases to an Apache Kafka topic
* Club membership discounts semi-randomly applied to smoothie purchases
* Add-on supplements semi-randomly applied to smoothie purchases
* Restocks low product inventories based on a minimum value
* Writes restocking activities to a second Apache Kafka topic

## Product Samples

Products roughly based on Tropical Smoothie menu
from [Fast Food Menu Prices](https://www.fastfoodmenuprices.com/tropical-smoothie-prices/). Last four columns, with `_`,
are used
to generate artificial product category and product weightings, which determine how frequently the products are
purchased in the simulation.

```csv
ID,Category,Item,Size,Price,Inventory,ContainsFruit,ContainsVeggies,ContainsNuts,ContainsCaffeine,_CatWeight,_ItemWeight,_TotalWeight,_RangeWeight
CS01,Classic Smoothies,Sunrise Sunset,24 oz.,4.99,75,TRUE,FALSE,FALSE,FALSE,3,2,6,6
CS02,Classic Smoothies,Kiwi Quencher,24 oz.,4.99,75,TRUE,FALSE,FALSE,FALSE,3,5,15,21
CS03,Classic Smoothies,Paradise Point,24 oz.,4.99,75,TRUE,FALSE,FALSE,FALSE,3,3,9,30
CS04,Classic Smoothies,Sunny Day,24 oz.,4.99,75,TRUE,FALSE,FALSE,FALSE,3,4,12,42
CS05,Classic Smoothies,Mango Magic,24 oz.,4.99,75,TRUE,FALSE,FALSE,FALSE,3,3,9,51
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
        "transaction_time": "2022-08-29 13:03:02.817920",
        "product_id": "SC02",
        "existing_level": 10,
        "new_level": 25
    },
    {
        "transaction_time": "2022-08-29 13:03:47.405038",
        "product_id": "SC04",
        "existing_level": 10,
        "new_level": 25
    },
    {
        "transaction_time": "2022-08-29 13:03:52.222737",
        "product_id": "IS01",
        "existing_level": 9,
        "new_level": 24
    },
    {
        "transaction_time": "2022-08-29 13:05:01.114076",
        "product_id": "SC05",
        "existing_level": 10,
        "new_level": 25
    },
    {
        "transaction_time": "2022-08-29 13:08:23.356092",
        "product_id": "SC02",
        "existing_level": 9,
        "new_level": 24
    }
]
```

## Commands

See [bitnami/kafka](https://hub.docker.com/r/bitnami/kafka) on Docker Hub for more information about running Kafka
locally using Docker.

```shell
docker-compose up -d

docker exec -it streaming-sales-generator_kafka_1 bash
```

To run the application:

```shell
python3 ./producer.py
python3 ./consumer.py
```

From within the Kafka container:

```shell
export BOOTSTRAP_SERVERS="localhost:9092"
export TOPIC_PURCHASES="smoothie.purchases"
export TOPIC_STOCKINGS="smoothie.stockings"

# delete topics
kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --delete --topic $TOPIC_PURCHASES
kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --delete --topic $TOPIC_STOCKINGS

# read topics from beginning
kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS --topic $TOPIC_PURCHASES --from-beginning
kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS --topic $TOPIC_STOCKINGS --from-beginning
```

---
_The contents of this repository represent my viewpoints and not of my past or current employers, including Amazon Web
Services (AWS). All third-party libraries, modules, plugins, and SDKs are the property of their respective owners. The
author(s) assumes no responsibility or liability for any errors or omissions in the content of this site. The
information contained in this site is provided on an "as is" basis with no guarantees of completeness, accuracy,
usefulness or timeliness._

