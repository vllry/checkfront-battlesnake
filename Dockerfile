FROM ubuntu:16.04


RUN apt-get update && \
	apt-get install -y python2.7 python-bottle python-gevent python-networkx
	
COPY . /opt/snake
WORKDIR /opt/snake/app

CMD python main.py
