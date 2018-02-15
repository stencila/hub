FROM ubuntu:16.04
MAINTAINER finlay@dragonfly.co.nz

RUN sed -i 's!archive.ubuntu.com/ubuntu/ xenial !nz.archive.ubuntu.com/ubuntu/ xenial !g' /etc/apt/sources.list
RUN sed -i 's!archive.ubuntu.com/ubuntu/ xenial-updates !nz.archive.ubuntu.com/ubuntu/ xenial-updates !g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y tzdata locales software-properties-common

RUN echo "Pacific/Auckland" > /etc/timezone
RUN ln -fs /usr/share/zoneinfo/Pacific/Auckland /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

RUN locale-gen en_NZ.UTF-8
RUN dpkg-reconfigure locales

ENV LANG en_NZ.utf8
ENV LANGUAGE en_NZ:en

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update

RUN apt-get install -y python3.6 python3.6-dev python3.6-venv libev-dev python3-pip

COPY director/requirements.txt /etc/requirements.txt
RUN pip3 install -r /etc/requirements.txt

RUN apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
