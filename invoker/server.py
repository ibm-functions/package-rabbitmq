#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""RabbitMQ queue listener and Cloud Function invoker.
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
import signal
import json
import time
import traceback
import logging

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
from concurrent.futures import FIRST_COMPLETED

from messenger import rabbitmq

import whisk

#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)

#Global variable to tell threads to shutdown
SHUTTING_DOWN = False


class MessageHandlerThread:
    """handle relay from rabbitmq to openwhisk"""
    def __init__(self, whisk_context, rabbit_context, subscribe, timeout_seconds, whisk_retries, action):
        self.rabbit = None
        self.invoker = None
        self.whisk_context = whisk_context
        self.rabbit_context = rabbit_context
        self.action = action
        self.subscribe = subscribe
        self.timeout_seconds = timeout_seconds
        self.whisk_retries = whisk_retries

    def send_to_whisk(self, recv_msg):
        """
            Callback to handle a received message, attempt to invoke an action
            with the message body as a parameter to the action

            Throws:
                No exceptions thrown

            Returns:
                True if the message was handled, otherwise False
        """

        retry = 0

        #LOGGER.info("Received message")

        try:
            recv_msg_size = len(recv_msg)
            if recv_msg_size > 5242880:
                #Need to ensure we dont send to much data whilst invoking the action
                raise BufferError("Message payload too large; {0} > 5242880 bytes!".format(recv_msg_size))

            #Its possible to have too many inflight whisk activations
            #So we'll need to retry if this error occurs

            while retry < self.whisk_retries and not SHUTTING_DOWN:
                if isinstance(recv_msg, bytes):
                    message = {'messages': [recv_msg.decode()]}
                else:
                    message = {'messages': [recv_msg]}

                result = self.invoker.invoke(json.dumps(message), self.action)
                if 'error' not in result:
                    break

                time.sleep(1)
                retry += 1

            LOGGER.info("Response: %r:%r retries...%r", self.action, retry, result)
        except Exception as expt:
            LOGGER.info("Message Error: %r", expt)
            LOGGER.info("Received: %d bytes", recv_msg_size)
            LOGGER.info("Received: %s", recv_msg[:1000])

        return retry == 0

    def stop(self):
        """
            Stops the RabbitMQ message consumption, effectively interrupting the blocking
                receive in the handler thread

            Throws:
                No exceptions thrown

            Returns:
                Nothing
        """
        self.rabbit.stop()

    def listen(self):
        """
            A thread, that starts the RabbitMQ message consumption

            Throws:
                No exceptions thrown

            Returns:
                Nothing
        """
        while not SHUTTING_DOWN:
            try:
                LOGGER.info("Connecting to OpenWhisk...")

                with whisk.WhiskInvoker(self.whisk_context) as self.invoker:
                    LOGGER.info("Connecting to RabbitMQ...")

                    with rabbitmq.RabbitClient(self.rabbit_context) as self.rabbit:
                        self.rabbit.start_queue(queue=rabbitmq.RabbitQueue(self.subscribe))

                        LOGGER.info("Waiting on %r...", self.subscribe)

                        #Blocks indefinitely
                        self.rabbit.receive(self.send_to_whisk, self.timeout_seconds)
                        LOGGER.info("Timed out or interrupted.")
            except Exception as expt:
                LOGGER.error("Listener Exception: %r", expt)
                traceback.print_exc()
                #Brief pause before re-connecting
                time.sleep(2)



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


def handle_sig(*args):
    """raise exception on signal"""
    raise KeyboardInterrupt()


def main():
    """main"""
    signal.signal(signal.SIGTERM, handle_sig)

    host = getenv('RABBIT_BROKER')
    port = int(getenv('RABBIT_PORT'))
    user = getenv('RABBIT_USER')
    password = getenv('RABBIT_PWD')
    vhost = getenv('RABBIT_VHOST')
    cert = getenv('CERT', 'cert.pem')
    subscribe = getenv('FEED_QUEUE')
    num_threads = min(int(getenv('RABBIT_CONNECTIONS', '1')), 32)
    timeout_seconds = int(getenv('SUBSCRIBE_TIMEOUT', '3600'))
    whisk_action = getenv('WHISK_ACTION')
    whisk_retries = int(getenv('WHISK_RETRIES', '10'))

    api_url = getenv('WHISK_URL', None)
    auth_key = getenv('WHISK_AUTH', None)
    namespace = getenv('WHISK_SPACE', None)

    LOGGER.info("Starting...")
    LOGGER.info(" %s, %d, %s, %s, %s.", host, port, user, vhost, subscribe)

    thread_pool = ThreadPoolExecutor(max_workers=num_threads)

    try:
        threads = {}
        rabbit_context = rabbitmq.RabbitContext(host, port, user, password, vhost, cert=cert)
        whisk_context = whisk.WhiskContext(api_url, auth_key, namespace)

        for _ in range(0, num_threads):
            handler = MessageHandlerThread(whisk_context, rabbit_context, subscribe, timeout_seconds, whisk_retries, whisk_action)
            future = thread_pool.submit(handler.listen)
            threads[future] = handler

        while True:
            try:
                stopped_threads, running_threads = wait(threads, timeout=3600, return_when=FIRST_COMPLETED)
                LOGGER.info("Running threads: %r, Stopped threads: %r", len(running_threads), len(stopped_threads))

                # Ordinarily, a thread should never finish; if one has, remove it and start replacement thread.
                for stopped_thread in stopped_threads:
                    LOGGER.error("Thread stopped; starting replacement...")
                    handler = threads[stopped_thread]
                    future = thread_pool.submit(handler.listen)
                    threads[future] = handler
                    del threads[stopped_thread]
            except KeyboardInterrupt:
                break
            except Exception as expt:
                LOGGER.error("Main Loop: %r", expt)
    except Exception as expt:
        LOGGER.error("Exception: %r", expt)
        traceback.print_exc()
    finally:
        LOGGER.info("Stopping...")

        global SHUTTING_DOWN
        SHUTTING_DOWN = True

        for future, handler in threads.items():
            handler.stop()

        thread_pool.shutdown()
        LOGGER.info("Stopped.")


if __name__ == '__main__':
    main()
