FROM alpine

RUN apk add --update python3

ADD requirements.txt /tmp/requirements.txt

RUN python3 -m pip install -r /tmp/requirements.txt

