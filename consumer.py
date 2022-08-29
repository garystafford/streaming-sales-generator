from kafka import KafkaConsumer
import json

# *** CONSTANTS ***
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_PURCHASE = 'smoothie.purchases'
TOPIC_STOCKING = 'smoothie.stockings'


def main():
    consumer = KafkaConsumer(
        TOPIC_STOCKING,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    for msg in consumer:
        print(msg)


if __name__ == '__main__':
    main()
