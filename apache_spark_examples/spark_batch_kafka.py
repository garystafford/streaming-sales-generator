# Purpose: Reads a batch of messages from a Kafka topic and aggregates to the console (stdout)
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
        .appName("kafka-batch-query") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("INFO")

    df_sales = read_from_kafka(spark)

    summarize_sales(df_sales)


def read_from_kafka(spark):
    options = {
        "kafka.bootstrap.servers":
            os.environ.get('BOOTSTRAP_SERVERS'),
        "subscribe":
            os.environ.get('TOPIC_PURCHASES'),
        "startingOffsets":
            "earliest",
        "endingOffsets":
            "latest"
    }

    if os.environ.get("AUTH_METHOD") == "sasl_scram":
        options["kafka.security.protocol"] = "SASL_SSL"
        options["kafka.sasl.mechanism"] = "SCRAM-SHA-512"
        options["kafka.sasl.jaas.config"] = os.environ.get("SASL_USERNAME")
        options["sasl_plain_password"] = \
            "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"{0}\" password=\"{1}\";".format(
                os.environ.get("SASL_USERNAME"), os.environ.get("SASL_PASSWORD"))

    df_sales = spark \
        .read \
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

    window = Window.partitionBy("product_id").orderBy("total_purchase")
    window_agg = Window.partitionBy("product_id")

    df_sales \
        .selectExpr("CAST(value AS STRING)") \
        .select(F.from_json("value", schema=schema).alias("data")) \
        .select("data.*") \
        .withColumn("row", F.row_number().over(window)) \
        .withColumn("quantity", F.count(F.col("quantity")).over(window_agg)) \
        .withColumn("sales", F.sum(F.col("total_purchase")).over(window_agg)) \
        .filter(F.col("row") == 1).drop("row") \
        .select("product_id",
                F.format_number("sales", 2).alias("sales"),
                F.format_number("quantity", 0).alias("quantity")) \
        .coalesce(1) \
        .orderBy(F.regexp_replace("sales", ",", "").cast("float"), ascending=False) \
        .write \
        .format("console") \
        .option("numRows", 25) \
        .option("truncate", False) \
        .save()


if __name__ == "__main__":
    main()
