# Instructions

```shell
docker cp *.json $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}"):/tmp/

docker exec -it $(docker container ls --filter  name=kafka_pinot-controller.1 --format "{{.ID}}") bash

bin/pinot-admin.sh AddTable \
  -tableConfigFile /tmp/purchases-config.json \
  -schemaFile /tmp/purchases-schema.json -exec
  ```