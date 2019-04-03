#!/usr/bin/env python
#author mark_purcell@ie.ibm.com

"""RabbitMQ message processor
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

from messenger import rabbitmq


def main(args):
    activation = os.getenv('__OW_ACTIVATION_ID', None)

    try:
        messages = 0

        cfg = ['broker_host', 'broker_vhost', 'broker_port',
               'broker_user', 'broker_password', 'publish_queue']
        for key in cfg:
            if args.get(key) is None:
                raise Exception('{} is missing'.format(key))

        host = args['broker_host']
        vhost = args['broker_vhost']
        port = args['broker_port']
        user = args['broker_user']
        password = args['broker_password']
        publish_queue = args['publish_queue']

        context = rabbitmq.RabbitContext(host, port, user, password, vhost)

        if 'messages' in args:
            with rabbitmq.RabbitClient(context) as client:
                client.start_queue(queue=rabbitmq.RabbitQueue(publish_queue))

                for msg in args['messages']:
                    messages += 1
                    print(msg)
                    client.publish(json.dumps({'count' : messages}))

        result = {'messages': messages}
    except Exception as err:
        result = {'result': str(err)}
        print("Error: %r" % err)

    result.update({"activation": activation})
    print(result)
    return result
