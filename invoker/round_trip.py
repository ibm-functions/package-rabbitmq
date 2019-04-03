#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""RabbitMQ round trip tester.
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""

import os
import json
import timeit
import logging
from messenger import rabbitmq

#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


def getenv(var, default=None):
    """ fetch environment variable,

        throws:
            exception if value and default are None

        returns:
            environment value
    """
    value = os.getenv(var, default)
    if not value:
        if not default:
            raise Exception(var + " environment variable must have a value")
        value = default
    return value


def main():
    """main"""
    host = getenv('RABBIT_BROKER')
    port = int(getenv('RABBIT_PORT'))
    user = getenv('RABBIT_USER')
    password = getenv('RABBIT_PWD')
    vhost = getenv('RABBIT_VHOST')
    cert = getenv('CERT', 'cert.pem')
    feed_queue = getenv('FEED_QUEUE')
    reply_queue = getenv('REPLY_QUEUE')

    messages = 10
    LOGGER.info("Starting...")

    context = rabbitmq.RabbitContext(host, port, user, password, vhost, cert=cert)

    try:
        start = timeit.default_timer()

        LOGGER.info("Sending requests to: %r", format(feed_queue))

        with rabbitmq.RabbitClient(context) as client:
            client.start_queue(queue=rabbitmq.RabbitQueue(feed_queue))
            message = {"serviceRequest" : "none"}

            for _ in range(0, messages):
                client.publish(json.dumps(message))

        LOGGER.info("Dispatched messages: %r", client.outbound)
        LOGGER.info("Now wait for replies on: %r", reply_queue)

        with rabbitmq.RabbitClient(context) as client:
            client.start_queue(queue=rabbitmq.RabbitQueue(reply_queue))
            client.receive(lambda x: None, max_messages=messages)

        LOGGER.info("Received messages: %r", client.inbound)
        stop = round(timeit.default_timer() - start, 2)
        LOGGER.info("Duration %r", stop)
        LOGGER.info("Done")
    except KeyboardInterrupt:
        LOGGER.info("Stopping")
    except Exception as err:
        LOGGER.info("Error %r", err)


if __name__ == '__main__':
    main()
