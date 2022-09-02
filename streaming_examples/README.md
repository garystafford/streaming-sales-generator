# Notes for Streaming Examples

Spark batch and streaming examples currently both use SASL/SCRAM authentication.

## Spark Commands

```shell
export BOOTSTRAP_SERVERS="b-1.localhost:9096,b-2.localhost:9096"
export TOPIC_PURCHASES="demo.purchases"
export SASL_USERNAME="foo"
export SASL_PASSWORD="bar"

spark-submit spark_batch_kafka.py

spark-submit spark_streaming_kafka.py
```

## Example Output: Spark Batch Aggregation

```txt
+----------+-----+--------+
|product_id|sales|quantity|
+----------+-----+--------+
|IS02      |98.06|15      |
|SF05      |95.58|10      |
|SC04      |77.25|9       |
|CS10      |70.71|10      |
|IS04      |66.71|9       |
|SC01      |62.87|8       |
|IS01      |58.67|9       |
|SF06      |56.69|8       |
|CS08      |56.17|10      |
|CS09      |53.38|7       |
+----------+-----+--------+
only showing top 10 rows
```

## Example Output: Spark Structured Streaming Microbatchs

```txt
-------------------------------------------
Batch: 7
-------------------------------------------
+----------+-----+------+-------------------+-------------------+
|product_id|sales|drinks|start              |end                |
+----------+-----+------+-------------------+-------------------+
|SF05      |43.49|4     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|SF06      |39.92|5     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|SC01      |34.93|4     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|SF02      |32.33|2     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|IS01      |30.88|5     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|CS08      |28.94|6     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|CS09      |28.93|3     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|CS10      |23.44|3     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|SF04      |20.35|3     |2022-09-02 16:10:00|2022-09-02 16:20:00|
|SF07      |19.36|3     |2022-09-02 16:10:00|2022-09-02 16:20:00|
+----------+-----+------+-------------------+-------------------+
only showing top 10 rows
```