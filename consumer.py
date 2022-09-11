# Purpose: Consumes all messages from Kafka topic for testing purposes
# Author:  Gary A. Stafford
# Date: 2022-08-29
# Instructions: Modify the configuration.ini file to meet your requirements.
#               Select the topic to view the messages from.

import configparser
import json

from kafka import KafkaConsumer

from config.kafka import get_configs

config = configparser.ConfigParser()
config.read("configuration/configuration.ini")

# *** CONFIGURATION ***
topic_products = config["KAFKA"]["topic_products"]
topic_purchases = config["KAFKA"]["topic_purchases"]
topic_stockings = config["KAFKA"]["topic_stockings"]


def main():
    consume_messages()


def consume_messages():
    # choose any or all topics
    topics = (topic_products, topic_purchases, topic_stockings)

    configs = get_configs()

    consumer = KafkaConsumer(
        *topics,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        **configs
    )

    for message in consumer:
        print(message.value)


if __name__ == "__main__":
    main()
