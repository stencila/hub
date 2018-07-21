FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get install -y \
      curl \
      python3 \
      python3-pip \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/stencila/cli/releases/download/v0.30.1/stencila-linux-x64.tar.gz | tar xvz \
 && mv stencila /usr/local/bin

RUN pip3 install gunicorn

RUN useradd -ms /bin/bash director
WORKDIR /home/director
USER director

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD --chown=director:director . .

CMD gunicorn wsgi --bind 0.0.0.0:8000
