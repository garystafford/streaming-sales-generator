import os

from pyflink.common import Row
from pyflink.common.serialization import JsonRowDeserializationSchema, JsonRowSerializationSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer


def datastream_api_demo():
    # 1. create a StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()
    # the sql connector for kafka is used here as it's a fat jar and could avoid dependency issues
    env.add_jars("file:///jars/flink-sql-connector-kafka-1.15.2.jar")

    # 2. create source DataStream
    deserialization_schema = JsonRowDeserializationSchema.builder() \
        .type_info(type_info=Types.ROW(
            [
                Types.SQL_TIMESTAMP(),
                Types.STRING()
            ]
        )
    ).build()

    kafka_source = FlinkKafkaConsumer(
        topics=os.environ.get('TOPIC_PURCHASES'),
        deserialization_schema=deserialization_schema,
        properties={'bootstrap.servers': os.environ.get('BOOTSTRAP_SERVERS')})

    ds = env.add_source(kafka_source)

    # 3. define the execution logic
    ds = ds.map(lambda a: Row(a % 4, 1), output_type=Types.ROW([Types.LONG(), Types.LONG()])) \
           .key_by(lambda a: a[0]) \
           .reduce(lambda a, b: Row(a[0], a[1] + b[1]))

    # 4. create sink and emit result to sink
    serialization_schema = JsonRowSerializationSchema.builder().with_type_info(
        type_info=Types.ROW([Types.LONG(), Types.LONG()])).build()
    kafka_sink = FlinkKafkaProducer(
        topic='test_sink_topic',
        serialization_schema=serialization_schema,
        producer_config={'bootstrap.servers': 'localhost:9092', 'group.id': 'test_group'})
    ds.add_sink(kafka_sink)

    # 5. execute the job
    env.execute('datastream_api_demo')


if __name__ == '__main__':
    datastream_api_demo()
