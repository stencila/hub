FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get install -y \
      python3 \
      python3-pip \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install gunicorn

RUN useradd -ms /bin/bash director
WORKDIR /home/director
USER director

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD --chown=director:director . .

CMD gunicorn director.wsgi -b 0.0.0.0:8000
