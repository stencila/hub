FROM ubuntu:18.10

ENV DEBIAN_FRONTEND noninteractive

# apt dependencies from gconf-service onwards are for puppeteer support for Stencila CLI
RUN apt-get update \
 && apt-get install -y \
      curl \
      python3 \
      python3-pip \
      gconf-service \
      libasound2 \
      libatk1.0-0 \
      libatk-bridge2.0-0 \
      libc6 \
      libcairo2 \
      libcups2 \
      libdbus-1-3 \
      libexpat1 \
      libfontconfig1 \
      libgcc1 \
      libgconf-2-4 \
      libgdk-pixbuf2.0-0 \
      libglib2.0-0 \
      libgtk-3-0 \
      libnspr4 \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      libstdc++6 \
      libx11-6 \
      libx11-xcb1 \
      libxcb1 \
      libxcomposite1 \
      libxcursor1 \
      libxdamage1 \
      libxext6 \
      libxfixes3 \
      libxi6 \
      libxrandr2 \
      libxrender1 \
      libxss1 \
      libxtst6 \
      ca-certificates \
      fonts-liberation \
      libappindicator1 \
      libnss3 \
      lsb-release \
      xdg-utils \
      wget

# Add the Nodesource repository and then install nodejs/npm. 
# Must be done after the previous step since curl is required
RUN curl -sL https://deb.nodesource.com/setup_13.x | bash - \
 && apt-get update \
 && apt-get install -y \
    nodejs \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN npm install @stencila/encoda@0.85.3

RUN pip3 install gunicorn

RUN useradd -ms /bin/bash director
WORKDIR /home/director
USER director

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD --chown=director:director . .

CMD gunicorn wsgi --bind 0.0.0.0:8000
