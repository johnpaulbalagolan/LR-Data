#!/bin/bash

if [ "$(uname)" == "Darwin" ]; then

    PIDS=()

    # Start Redis
    pushd ../conf/redis > /dev/null 2>&1
    redis-server redis.homebrew.conf &
    PIDS+=("$!")
    popd

    # Start RabbitMQ
    rabbitmq-server &
    PIDS+=("$!")

    elasticsearch -f -Des.config=../conf/elasticsearch/elasticsearch.homebrew.yml
    PIDS+=("$!")

    kill ${PIDS[*]}

    wait

    echo "Services Stopped"

else
    echo "Sorry. For now this script is only configured for OSX with services installed via homebrew"
fi
