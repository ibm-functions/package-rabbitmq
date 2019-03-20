# RabbitWhisker
This project is an event source for IBM Cloud Functions, where the events originate from a RabbitMQ queue.


## Overview
This document describes a mechanism (called RabbitWhisker) to provide a feed from RabbitMQ (IBM Cloud - [Messages for RabbitMQ](https://console.bluemix.net/catalog/services/messages-for-rabbitmq)) to IBM Cloud Functions, in essence, relaying messages from a RabbitMQ queue, to an IBM Cloud Function.
There are two separate modules provided as part of the solution. First, a listener component that subscribes to a RabbitMQ queue, retrieves a message, and invokes an IBM Cloud Function. Second, an IBM Cloud function that will be invoked by the listener. Also provided is a sample client application that publishes messages to a RabbitMQ queue. An example of how to respond to this client application via a RabbitMQ queue is also coded in the Cloud function.

These modules have the following dependencies, which are assumed to be satisfied:

```
- A RabbitMQ service is provisioned (on IBM Cloud).
- Service credentials for this RabbitMQ service are created and available.
- The IBM Cloud CLI is installed.
- An IBM Cloud organisation and space are targeted (see bx target command).
- Docker 18.09 or higher is installed.
- Python 3.5 or higher is installed.
```

## Installation
First, the local environment must be configured, by providing the following environment variables.

|Name|Type|Description|
|---|---|---|
|RABBIT_BROKER|URL|The base URL for the RabbitMQ service|
|RABBIT_PORT|String|The port number for the RabbitMQ service|
|RABBIT_VHOST|String|The virtual host, often '/'|
|RABBIT_USER|String|Username for the RabbitMQ service|
|RABBIT_PWD|String|Password for the RabbitMQ service|
|CERT|String|Path to the certificate PEM file for the RabbitMQ service|
|REPLY_QUEUE|String|Queue to retrieve messages from, used by the client application|
|FEED_QUEUE|String|Queue to retrieve messages from, used by the feed listener|
|WHISK_ACTION|String|The IBM Cloud Function name to invoke on receipt of a message|
|WHISK_SPACE|String|The full namespace for IBM Cloud Function invocation|
|WHISK_URL|URL|The base URL for IBM Cloud Functions|
|WHISK_AUTH|String|Authentication token for accessing IBM Cloud Functions|

An `env.sh` script is provided, which can be edited to specify these variables.

To populate the RabbitMQ variables, connection details to the RabbitMQ service are required. 
For the IBM Cloud - [Messages for RabbitMQ](https://console.bluemix.net/catalog/services/messages-for-rabbitmq) service, see [here](CREDENTIAL.md) for some details on how to retrieve these credentials.

The `REPLY_QUEUE` and `FEED_QUEUE` environment variables are queue names, for example, `FEED_QUEUE` could be 'requests' and `REPLY_QUEUE` could be 'replies'.

### Cloud Functions Credentials

Now details for the IBM Cloud Functions service are retrieved, which are available via:

```
bx plugin install cloud-functions
bx wsk property get
```

The output will look similar to:

```
whisk auth		xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
whisk API host		eu-de.functions.cloud.ibm.com
whisk API version	v1
whisk namespace		_
whisk CLI version	2019-02-04T22:28:01+00:00
whisk API build		2019-03-07T16:26:34Z
whisk API build number	whisk-build-11573
```

Note: the `WHISK_SPACE` variable is a combination of `bx organisation` + `whisk namespace` + `bx space`, where `bx organisation` and `bx space` are found from the `bx target` command, and `whisk namespace` is found from the `bx wsk property get` command (`whisk namespace` above). For example:
```
WHISK_SPACE=myorg_myspace
```

The `WHISK_URL` variable is a combination of `whisk API host` + `/api/` + `whisk API version`, from the `bx wsk property get` command. For example: from above: 
```
WHISK_URL=https://eu-de.functions.cloud.ibm.com/api/v1
```

## Test
At this stage there should be an `env.sh` script with the required environment variables specified. 

The connection details in these variables can now be tested. But first, the appropriate Python package dependencies must be installed.

```
pip3 install -r invoker/requirements.txt
./test_connect.sh
```

If the credentials are correct, the test should successfully connect to the RabbitMQ service. If this fails, the credentials may not be specified correctly.

## Build and deploy
Now the listner and cloud function can be built and deployed. First, deploy the cloud function. This function is invoked by the RabbitMQ listener, and upon invocation, publishes a response to a different RabbitMQ queue, the `REPLY_QUEUE`.

```
cd action
./install.sh
cd ..
```

Ouput similar to the following should appear:

```
  adding: __main__.py (deflated 58%)
  adding: messenger/rabbitmq.py (deflated 69%)
ok: updated action RabbitFeedEndpoint
```


Next, the docker image that will run the RabbitMQ listener can be built.

```
docker build -t rabbitmq_feed:latest -t rabbitmq_feed:$(cat invoker/VERSION) .
```

And then started:

```
./start_listener.sh
```

Logs from the running container can be viewed with `docker logs <container-id>`.


## Running the end-to-end application
Upon successful completion of the above steps, there is a deployed cloud function ready to be invoked and a running RabbitMQ listener waiting for messages. The end-to-end client application can now be started, which publishes messsages to the `FEED_QUEUE`, and waits for the appropriate number of responses on the `REPLY_QUEUE`.

```
./round_trip.sh
```

Ouput similar to the following will be produced:

```
2019-03-19 12:07:04.129 INFO   root 139834587285248 :: Starting...
2019-03-19 12:07:04.129 INFO   root 139834587285248 :: Sending requests to: requests
.
.
.
2019-03-19 12:07:04.886 INFO   root 139834587285248 :: Dispatched messages: 10
2019-03-19 12:07:04.886 INFO   root 139834587285248 :: Now wait for replies on: responses
.
.
.
2019-03-19 12:07:05.908 INFO   root 139834587285248 :: Received messages: 10
2019-03-19 12:07:05.908 INFO   root 139834587285248 :: Duration 1.78
2019-03-19 12:07:05.910 INFO   root 139834587285248 :: Done
```


## References
RabbitWhisker was developed during the GOFLEX H2020 project.

The project Generalized Operational FLEXibility for Integrating Renewables in the Distribution Grid (GOFLEX) has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 731232. ![HorizonH2020](EU.png)


