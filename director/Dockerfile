FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV CONVERT_VERSION v0.36.0

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

RUN curl -Lo /tmp/convert.tar.gz https://github.com/stencila/convert/releases/download/${CONVERT_VERSION}/convert-linux-x64.tar.gz && \
    tar xvf /tmp/convert.tar.gz && \
    rm -f /tmp/convert.tar.gz && \
    echo "Installing stencila-convert to /usr/local/bin/stencila-convert-${CONVERT_VERSION}/" && \
    mkdir -p /usr/local/bin/stencila-convert-${CONVERT_VERSION} && \
    mv -f stencila-convert /usr/local/bin/stencila-convert-${CONVERT_VERSION} && \
    /usr/local/bin/stencila-convert-${CONVERT_VERSION}/stencila-convert --version && \
    echo "Pointing stencila-convert to /usr/local/bin/stencila-convert-${CONVERT_VERSION}/stencila-convert" && \
    ln -sf stencila-convert-${CONVERT_VERSION}/stencila-convert /usr/local/bin/stencila-convert

RUN pip3 install gunicorn

RUN useradd -ms /bin/bash director
WORKDIR /home/director
USER director

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD --chown=director:director . .

CMD gunicorn wsgi --bind 0.0.0.0:8000
