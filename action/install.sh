#!/bin/bash
#Author: Mark Purcell (markpurcell@ie.ibm.com)
#Assumes the user is already logged in to Bluemix
#And that an organisation/space is targeted
#by running "bx target -o ORG -s SPACE"

source ../env.sh

VERSION=$(cat VERSION)

ln -s ../messenger
cp client.py __main__.py
zip -r $WHISK_ACTION-$VERSION.zip __main__.py messenger/rabbitmq.py
rm __main__.py
rm messenger

bx wsk action update --kind python:3.7 --param debug true --param broker_host $RABBIT_BROKER --param broker_vhost $RABBIT_VHOST --param broker_port $RABBIT_PORT --param broker_user $RABBIT_USER --param broker_password $RABBIT_PWD --param publish_queue $REPLY_QUEUE $WHISK_ACTION $WHISK_ACTION-$VERSION.zip


