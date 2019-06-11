FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV STENCILA_CLI_VERSION v0.30.2

RUN apt-get update \
 && apt-get install -y \
      curl \
      python3 \
      python3-pip \
      libx11-6 \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install gunicorn

RUN useradd -ms /bin/bash director
WORKDIR /home/director
USER director

RUN curl -L https://raw.githubusercontent.com/stencila/stencila/master/install.sh | bash -s ${STENCILA_CLI_VERSION}

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD --chown=director:director . .

CMD gunicorn wsgi --bind 0.0.0.0:8000
