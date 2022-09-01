# Purpose: Consumes all messages from Kafka topic for testing purposes
# Author:  Gary A. Stafford
# Date: 2022-08-29
# Instructions: Modify the configuration.ini file to meet your requirements.
#               Select the topic to view the messages from.

import configparser
import json

from kafka import KafkaConsumer, KafkaProducer

config = configparser.ConfigParser()
config.read('configuration.ini')

# *** CONFIGURATION ***
bootstrap_servers = config['KAFKA']['bootstrap_servers']
topic_purchases = config['KAFKA']['topic_purchases']
topic_rewrite = 'demo.rewrite'


def main():
    consumer = KafkaConsumer(
        topic_purchases,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    for message in consumer:
        print(message.value)
        publish_to_kafka(message.value)


def publish_to_kafka(message):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(vars(v)).encode('utf-8')
    )
    producer.send(topic_rewrite, value=message)
    print(message)


if __name__ == '__main__':
    main()
