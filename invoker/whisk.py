#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""Cloud Function invoker.
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

import json
import requests


class WhiskContext:
    """WhiskContext"""
    def __init__(self, api_url, auth_key, namespace):
        self.url = api_url + '/namespaces/' + namespace + '/actions/'
        self.user_pass = auth_key.split(':')


class WhiskInvoker:
    """WhiskInvoker"""
    def __init__(self, context, blocking='false', result='false'):
        self.context = context
        self.params = {'blocking': blocking, 'result': result}
        self.start()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        """
            Establish a connection to Openwhisk

            Throws:
                Exception thrown if connection cannot be established

            Returns:
                Nonee
        """

        self.session = requests.Session()
        self.session.auth = (self.context.user_pass[0], self.context.user_pass[1])
        self.session.headers.update({'content-type': 'application/json'})

    def close(self):
        """
            Closes the connection to Openwhisk

            Throws:
                Exception thrown if connection cannot be closed

            Returns:
                Nonee
        """
        self.session.close()

    def invoke(self, json_msg, action):
        """
            Invokes an Openwhisk action, catching all exceptions

            Throws:
                No exception thrown

            Returns:
                The response from Openwhisk, or a dict containing an error
        """

        try:
            response = self.session.post(self.context.url + action, data=json_msg, params=self.params)
        except Exception as expt:
            #Something went wrong - could be a general error
            #or under high load, too many in-flight activations
            #Retry policy is the responsibility of the caller
            self.close()
            self.start()
            return {'error': str(expt)}

        # It's possible that the OW action is not available
        # in which case there will be an "error" entry in the response dict
        return json.loads(response.text)
