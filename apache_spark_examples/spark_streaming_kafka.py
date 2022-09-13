# Purpose: Reads a stream of messages from a Kafka topic and
#          writes a stream of aggregations over sliding event-time window to console (stdout)
# References: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
# Author:  Gary A. Stafford
# Date: 2022-09-02
# Note: Expects (4) environment variables: BOOTSTRAP_SERVERS, TOPIC_PURCHASES, SASL_USERNAME, SASL_PASSWORD

import os
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, \
    StringType, FloatType, TimestampType, BooleanType
from pyspark.sql.window import Window


def main():
    spark = SparkSession \
        .builder \
        .appName("kafka-streaming-query") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("INFO")

    df_sales = read_from_kafka(spark)

    summarize_sales(df_sales)


def read_from_kafka(spark):
    options = {
        "kafka.bootstrap.servers":
            os.environ.get("BOOTSTRAP_SERVERS"),
        "subscribe":
            os.environ.get("TOPIC_PURCHASES"),
        "startingOffsets":
            "earliest"
    }

    if os.environ.get("AUTH_METHOD") == "sasl_scram":
        options["kafka.security.protocol"] = "SASL_SSL"
        options["kafka.sasl.mechanism"] = "SCRAM-SHA-512"
        options["kafka.sasl.jaas.config"] = os.environ.get("SASL_USERNAME")
        options["sasl_plain_password"] = \
            "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"{0}\" password=\"{1}\";".format(
                os.environ.get("SASL_USERNAME"), os.environ.get("SASL_PASSWORD"))

    df_sales = spark \
        .readStream \
        .format("kafka") \
        .options(**options) \
        .load()

    return df_sales


def summarize_sales(df_sales):
    schema = StructType([
        StructField("transaction_time", TimestampType(), False),
        StructField("transaction_id", IntegerType(), False),
        StructField("product_id", StringType(), False),
        StructField("price", FloatType(), False),
        StructField("quantity", IntegerType(), False),
        StructField("is_member", BooleanType(), True),
        StructField("member_discount", FloatType(), True),
        StructField("add_supplements", BooleanType(), True),
        StructField("supplement_price", FloatType(), True),
        StructField("total_purchase", FloatType(), False),
    ])

    ds_sales = df_sales \
        .selectExpr("CAST(value AS STRING)") \
        .select(F.from_json("value", schema=schema).alias("data")) \
        .select("data.*") \
        .withWatermark("transaction_time", "10 minutes") \
        .groupBy("product_id",
                 F.window("transaction_time", "10 minutes", "5 minutes")) \
        .agg(F.sum("total_purchase"), F.count("quantity")) \
        .orderBy(F.col("window").desc(),
                 F.col("sum(total_purchase)").desc()) \
        .select("product_id",
                F.format_number("sum(total_purchase)", 2).alias("sales"),
                F.format_number("count(quantity)", 0).alias("drinks"),
                "window.start", "window.end") \
        .coalesce(1) \
        .writeStream \
        .queryName("streaming_to_console") \
        .trigger(processingTime="1 minute") \
        .outputMode("complete") \
        .format("console") \
        .option("numRows", 10) \
        .option("truncate", False) \
        .start()

    ds_sales.awaitTermination()


if __name__ == "__main__":
    main()
