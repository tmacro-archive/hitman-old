FROM tmac/python:2

ADD requirements.txt /tmp/requirements.txt

RUN apk_add zeromq && \
	apk_add --virtual build gcc python-dev build-base && \
	pip install -r /tmp/requirements.txt && \
	apk del build

ADD . /app
ADD ./s6 /etc

