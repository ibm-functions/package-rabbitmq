#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""Test RabbitMQ connection.
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
import logging
from messenger import rabbitmq

#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


def getenv(var, default=None):
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

    success = False
    context = rabbitmq.RabbitContext(host, port, user, password, vhost, cert=cert)

    try:
        LOGGER.info("Connecting...")

        with rabbitmq.RabbitClient(context) as _:
            success = True
            LOGGER.info("Success.")
    except KeyboardInterrupt:
        LOGGER.info("Stopping")
    except Exception as expt:
        LOGGER.info("Error: %r", expt)

    if success:
        LOGGER.info("SUCCESS - connection to the RabbitMQ service verified.")
    else:
        LOGGER.info("FAILED - connection to the RabbitMQ service not verified.")

if __name__ == '__main__':
    main()
