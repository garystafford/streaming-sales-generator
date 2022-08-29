# Streaming Smoothie Sales Generator

Highly-configurable data generator, which streams sales transactions to Apache Kafka for demonstration purposes. Can be used to demonstrate streaming data analytics tools, such as Apache Spark Structured Streaming, Apache Flink, Apache Pinot, Databricks, Amazon Kinesis Data Analytics

## Highlights

* All configuration in `configuration.ini` file
* Nothing is completely random - all purchase variables are weighted
* Over 25 products: descriptions, inventories, product weightings
* Generates streaming purchases
* Writes the purchases to an Apache Kafka topic
* Restocks low product inventories based on minimum value
* Writes restocking activity to a second Apache Kafka topic
* Club membership discounts semi-randomly applied to purchases
* Add-on supplements semi-randomly applied to purchases

## Product Samples

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

See https://hub.docker.com/r/bitnami/kafka for more information about running Kafka locally using Docker.

```shell
docker-compose up -d

docker exec -it streaming-sales-generator_kafka_1 bash
```

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

```shell
python3 ./producer.py
python3 ./consumer.py
```