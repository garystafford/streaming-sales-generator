# Streaming Sales Generating

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
```