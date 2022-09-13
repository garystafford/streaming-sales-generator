# Notes for Streaming Examples

Spark batch and streaming examples currently both use SASL/SCRAM authentication.

## Spark Commands

```shell

# Install packages on AWS EMR
sudo yum install git vim wget

# Install packages in Bitnami container
docker exec -it -u 0 $(docker container ls --filter  name=streaming-stack_spark.1 --format "{{.ID}}") bash
apt-get update && apt-get install git vim wget

python3 -m pip install kafka-python

wget https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar
wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.1/kafka-clients-2.8.1.jar
wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar
wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.3.0/spark-token-provider-kafka-0-10_2.12-3.3.0.jar
mv *.jar /opt/bitnami/spark/jars/

# Run Spark jobs Bitnami container
SPARK_CONTAINER=$(docker container ls --filter  name=streaming-stack_spark.1 --format "{{.ID}}")
docker cp streaming_examples/ ${SPARK_CONTAINER}:/home/

docker exec -it $(docker container ls --filter  name=streaming-stack_spark.1 --format "{{.ID}}") bash
cd /home/streaming_examples/apache_spark_docker_container/

export BOOTSTRAP_SERVERS="localhost:9092"

# Bitnami container
export BOOTSTRAP_SERVERS="kafka:29092"

export TOPIC_PURCHASES="demo.purchases"

# optional: SASL/SCRAM
export SASL_USERNAME="foo"
export SASL_PASSWORD="bar"

git clone https://github.com/garystafford/streaming-sales-generator.git
cd streaming-sales-generator/


spark-submit spark_batch_kafka.py

spark-submit spark_streaming_kafka.py
```

## Example Output: Spark Batch Aggregation

```txt
+----------+------+--------+
|product_id|sales |quantity|
+----------+------+--------+
|IS02      |321.85|43      |
|SC04      |261.06|28      |
|SF05      |221.51|27      |
|IS03      |197.79|29      |
|CS05      |191.42|26      |
|SF07      |183.18|24      |
|CS10      |180.34|25      |
|CS08      |178.29|29      |
|IS04      |168.75|22      |
|SC01      |163.44|21      |
+----------+------+--------+
only showing top 10 rows
```

## Example Output: Spark Structured Streaming Microbatch

```txt
-------------------------------------------
Batch: 10
-------------------------------------------
+----------+-----+------+-------------------+-------------------+
|product_id|sales|drinks|start              |end                |
+----------+-----+------+-------------------+-------------------+
|SF05      |40.11|4     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|SC04      |39.92|4     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|IS02      |21.96|4     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|SC01      |19.96|3     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|IS04      |16.47|3     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|CS06      |16.26|3     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|CS08      |15.26|2     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|CS09      |14.47|3     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|SC05      |13.97|2     |2022-09-02 16:15:00|2022-09-02 16:25:00|
|CS02      |9.98 |2     |2022-09-02 16:15:00|2022-09-02 16:25:00|
+----------+-----+------+-------------------+-------------------+
only showing top 10 rows
```
