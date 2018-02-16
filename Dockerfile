FROM ubuntu:16.04
MAINTAINER finlay@dragonfly.co.nz

RUN sed -i 's!archive.ubuntu.com/ubuntu/ xenial !nz.archive.ubuntu.com/ubuntu/ xenial !g' /etc/apt/sources.list
RUN sed -i 's!archive.ubuntu.com/ubuntu/ xenial-updates !nz.archive.ubuntu.com/ubuntu/ xenial-updates !g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y tzdata locales software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.6 python3.6-dev python3.6-venv libev-dev python3-pip
RUN apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /app
WORKDIR /app
COPY director/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

ADD director /app 

CMD /app/wsgi.py

