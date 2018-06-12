FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get install -y \
      python3.6 \
      python3.6-dev \
      python3.6-venv \
      python3-pip \
      libev-dev \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

ADD . /app

RUN python3 manage.py makemigrations director
RUN python3 manage.py migrate

CMD /app/wsgi.py
