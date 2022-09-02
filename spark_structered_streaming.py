# Purpose: Reads stream of messages from Kafka topic and
#          writes stream of aggregations over sliding event-time window to console (stdout)
# References: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
# Author:  Gary A. Stafford
# Date: 2022-09-02
# Note: Requires --bootstrap_servers argument

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, \
    StringType, FloatType, TimestampType, BooleanType


def main():
    spark = SparkSession \
        .builder \
        .appName("streaming-kafka") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("INFO")

    df_sales = read_from_kafka(spark)

    summarize_sales(df_sales)


def read_from_kafka(spark):
    options_read = {
        "kafka.bootstrap.servers":
            "localhost:9092",
        "subscribe":
            "demo.purchases",
        "startingOffsets":
            "earliest"
    }

    df_sales = spark \
        .readStream \
        .format("kafka") \
        .options(**options_read) \
        .load()

    return df_sales


def summarize_sales(df_sales):
    schema = StructType([
        StructField("transaction_time", TimestampType(), False),
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
        .selectExpr("CAST(value AS STRING)", "timestamp") \
        .select(F.from_json("value", schema=schema).alias("data"), "timestamp") \
        .select("data.*", "timestamp") \
        .withWatermark("timestamp", "10 minutes") \
        .groupBy("product_id",
                 F.window("timestamp", "10 minutes", "5 minutes")) \
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
