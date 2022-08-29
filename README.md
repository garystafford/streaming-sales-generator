# Streaming Smoothie Sales Generator

## Highlights

* Over 25 smoothie products: descriptions, inventories, weightings
* Generate streaming smoothie purchases from a product list
* Write the purchases to an Apache Kafka topic
* Restock low product inventories
* Write restocking activity to a second Apache Kafka topic

## Transaction Sample

```json
{
    "transaction_time": "2022-08-29 02:14:17.980703",
    "product_id": "CS02",
    "price": 4.99,
    "quantity": 1,
    "is_member": false,
    "member_discount": 0.0,
    "add_supplements": false,
    "supplement_price": 0.0,
    "total_purchase": 6.98
}
```

## Commands

```shell
docker-compose up -d

docker exec -it streaming-sales-generator_kafka_1 bash

export BOOTSTRAP_SERVERS="localhost:9092"
export TOPIC_PURCHASE="smoothie.purchases"
export TOPIC_STOCKING="smoothie.stockings"

kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --delete --topic $TOPIC_PURCHASE
kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --delete --topic $TOPIC_STOCKING

kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS --topic $TOPIC_PURCHASE --from-beginning
kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS --topic $TOPIC_STOCKING --from-beginning

python3 ./generator.py
```