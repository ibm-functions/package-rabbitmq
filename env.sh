#!/bin/bash
#Author: Mark Purcell (markpurcell@ie.ibm.com)

#See output of "AMQPS" for "bx cdb deployment-connections YOURDEPLOYMENT" to help specify the following
#Or view "Service Credentials" on the IBM Cloud Dashboard for your RabbitMQ deployment
export RABBIT_BROKER=''            #Your RabbitMQ host
export RABBIT_PORT=                #Your RabbitMQ port number
export RABBIT_VHOST=''             #Your RabbitMQ virtual host, Often '/'
export RABBIT_USER=''              #Your RabbitMQ user
export RABBIT_PWD=''               #Your RabbitMQ password
export CERT=$PWD/cert.pem          #Certificate for RabbitMQ host
export FEED_QUEUE='request'        #Queue name for Listener to subscribe on
export REPLY_QUEUE='response'      #Queue name for Openwhisk action to reply on

#See output of "bx wsk property get" to help specify the following
export WHISK_ACTION='RabbitFeedEndpoint'
export WHISK_SPACE=                       #Your Openwhisk namespace
export WHISK_AUTH=''                      #Your Openwhisk auth key
export WHISK_URL=''                       #Your Openwhisk URL


