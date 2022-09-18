# Instructions

Commands to run from host that is running Apache Pinot/Kafka Docker Swarm stack.

```shell
# clone project locally
git clone https://github.com/garystafford/streaming-sales-generator.git
cd streaming-sales-generator/

# generate some messages
python3 -m pip install kafka-python
python3 ./producer.py

# deploy pinot/kafka stack
docker stack deploy pinot-kafka --compose-file apache-pinot-kafka-stack.yml

# create new pinot table
cd ~/streaming-sales-generator/apache_pinot_examples
docker cp purchases-schema.json $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}"):/tmp/
docker cp purchases-config.json $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}"):/tmp/

docker exec -it $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}") bash

bin/pinot-admin.sh AddTable \
  -tableConfigFile /tmp/purchases-config.json \
  -schemaFile /tmp/purchases-schema.json -exec
```

Sample SQL Statements

```sql
SELECT
  product_id,
  SUM(quantity) AS quantity,
  ROUND(SUM(total_purchase), 1) AS sales,
  MAX(total_purchase) AS max_sale
FROM
  purchases
GROUP BY
  product_id
ORDER BY
  sales DESC
LIMIT
  10;
```

## Preview

![Pinot UI](screengrabs/pinot_ui.png)

## Build Apache Superset for Pinot

```shell
cd apache_superset
export TAG=0.44.0
docker build \
  -f Dockerfile \
  -t garystafford/superset-pinot:${TAG} .

docker push garystafford/superset-pinot:${TAG}

SUPERSET_CONTAINER=$(docker container ls --filter  name=pinot-kafka_superset.1 --format "{{.ID}}")

docker exec -it ${SUPERSET_CONTAINER} superset fab create-admin \
  --username admin \
  --firstname Superset \
  --lastname Admin \
  --email admin@superset.com \
  --password admin

docker exec -it ${SUPERSET_CONTAINER} superset db upgrade

# optional
# docker exec -it ${SUPERSET_CONTAINER} superset load_examples

docker exec -it ${SUPERSET_CONTAINER} superset init


pinot+http://pinot-broker:8099/query?controller=http://pinot-controller:9000/debug=true

pinot+http://<pinot-broker-host>:<pinot-broker-port>/query?controller=http://<pinot-controller-host>:<pinot-controller-port>/``

pinot://pinot-broker:8099/pql?server=http://pinot-controller:9000/debug=true

pinot://CONTROLLER:5436/query?server=http://CONTROLLER:5983/

pinot+<pinot-broker-protocol>://<pinot-broker-host>:<pinot-broker-port><pinot-broker-path>?controller=<pinot-controller-protocol>://<pinot-controller-host>:<pinot-controller-port>/
pinot://pinot-broker:9000/pql?server=http://pinot-controller:9000/debug=true
pinot+http://<pinot-broker-host>:<pinot-broker-port>/query?controller=http://<pinot-controller-host>:<pinot-controller-port>/
```
