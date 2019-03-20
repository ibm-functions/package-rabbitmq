## RabbitMQ Credentials

To obtain RabbitMQ credentials, connection details to the RabbitMQ service are required. 

It is assumed that the IBM Cloud - [Messages for RabbitMQ](https://console.bluemix.net/catalog/services/messages-for-rabbitmq) service is used. 
Note: *After this service is provisioned the password for the `admin` user must be changed.* This can be done on the IBM Cloud Dashboard for the service, `Settings tab / Change Password panel` or with the IBM Cloud CLI as follows:

```
bx plugin install cloud-databases
bx cdb user-password "YOUR RABBITMQ SERVICE" admin <newpassword>
```

The remaining credentials are obtained from the IBM Cloud by using the IBM Cloud CLI plugin.

```
bx cdb deployment-connections "YOUR RABBITMQ SERVICE"
```

See the `AMQPS` output for the relevant RabbitMQ credentials, and use the `admin` user with the password already created. Note: the port number must be the AMQPS port, not a HTTPS port.

The SSL certificate for the service can be retrived as follows:

```
bx cdb deployment-cacert "YOUR RABBITMQ SERVICE" > cert.pem
```

