FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get install -y \
      curl \
      python3.6 \
      python3.6-dev \
      python3.6-venv \
      python3-pip \
      libev-dev \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/stencila/cli/releases/download/v0.29.3/stencila-linux-x64.tar.gz | tar xvz \
 && mv stencila /usr/local/bin

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

ADD . /app

RUN python3 manage.py makemigrations director
RUN python3 manage.py migrate

CMD /app/wsgi.py
