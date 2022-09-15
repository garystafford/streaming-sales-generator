# Instructions

Commands to run from AWS EC2 host, running Apache Pinot/Kafka Docker Swarm stack.

```shell
git clone https://github.com/garystafford/streaming-sales-generator.git
cd streaming-sales-generator/

python3 -m pip install kafka-python
python3 ./producer.py

docker stack deploy pinot-kafka --compose-file apache-pinot-kafka-stack.yml

cd /home/ec2-user/streaming-sales-generator/apache_pinot_examples
docker cp purchases-schema.json $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}"):/tmp/
docker cp purchases-config.json $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}"):/tmp/

docker exec -it $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}") bash

bin/pinot-admin.sh AddTable \
  -tableConfigFile /tmp/purchases-config.json \
  -schemaFile /tmp/purchases-schema.json -exec
```
