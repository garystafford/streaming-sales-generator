# Purpose: Consumes all messages from Kafka topic for testing purposes
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
auth_method = config['KAFKA']['auth_method']
sasl_username = config['KAFKA']['sasl_username']
sasl_password = config['KAFKA']['sasl_password']

topic_products = config['KAFKA']['topic_products']
topic_purchases = config['KAFKA']['topic_purchases']
topic_stockings = config['KAFKA']['topic_stockings']


def main():
    consume_messages()


def consume_messages():
    if auth_method == 'sasl_scram':
        configs = {
            'security_protocol':
                'SASL_SSL',
            'sasl_mechanism':
                'SCRAM-SHA-512',
            'sasl_plain_username':
                sasl_username,
            'sasl_plain_password':
                sasl_password
        }
    else:
        configs = {}

    # choose any or all topics
    topics = (topic_products, topic_purchases, topic_stockings)

    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        **configs
    )

    for message in consumer:
        print(message.value)


if __name__ == '__main__':
    main()
