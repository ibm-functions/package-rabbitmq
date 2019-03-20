#!/bin/bash
#Author: Mark Purcell (markpurcell@ie.ibm.com)

source env.sh

#Can increase the number of "listeners" to RabbitMQ if necessary
#export RABBIT_CONNECTIONS=4

#Start the RabbitMQ listener container
docker run -d --rm --name rabbitmq_feed -e RABBIT_BROKER="$RABBIT_BROKER" -e RABBIT_PORT="$RABBIT_PORT" -e RABBIT_VHOST="$RABBIT_VHOST" -e RABBIT_USER="$RABBIT_USER" -e RABBIT_PWD="$RABBIT_PWD" -e RABBIT_CONNECTIONS="$RABBIT_CONNECTIONS" -e FEED_QUEUE="$FEED_QUEUE" -e WHISK_SPACE="$WHISK_SPACE" -e WHISK_AUTH="$WHISK_AUTH" -e WHISK_URL="$WHISK_URL" -e WHISK_ACTION="$WHISK_ACTION" rabbitmq_feed
