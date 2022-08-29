# Streaming Sales Generating

```shell
docker-compose up -d
docker exec -it streaming-sales-generator_kafka_1 bash
kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic purchases --from-beginning

kafka-topics.sh --bootstrap-server kafka:9092 --delete --topic purchases
```