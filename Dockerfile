FROM alpine:latest

# Document who is responsible for this image
MAINTAINER Mark Purcell "markpurcell@ie.ibm.com"

# Install just the Python runtime (no dev)
RUN apk add --update \
    python3 \
    py3-pip \
 && rm -rf /var/cache/apk/*

WORKDIR /app

ADD cert.pem /app/
ADD invoker/requirements.txt /app
RUN pip3 install -r requirements.txt

ADD invoker/*.py /app/
RUN mkdir -p /app/messenger
ADD messenger/rabbitmq.py /app/messenger

ENTRYPOINT [ "python3", "server.py" ]

