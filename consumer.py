# Purpose: Consume messages from Kafka topic
# Author:  Gary A. Stafford
# Date: 2022-08-29
# Instructions: Modify the configuration.ini file to meet your requirements.
#               Select the topic to view the messages from.

import configparser
import json

from kafka import KafkaConsumer


config = configparser.ConfigParser()
config.read('configuration.ini')

# *** CONFIGURATION ***
bootstrap_servers = config['KAFKA']['bootstrap_servers']
topic_products = config['KAFKA']['topic_products']
topic_purchases = config['KAFKA']['topic_purchases']
topic_stockings = config['KAFKA']['topic_stockings']


def main():
    consumer = KafkaConsumer(
        topic_products,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
    )
    for message in consumer:
        data = message.value
        print(data)


if __name__ == '__main__':
    main()
