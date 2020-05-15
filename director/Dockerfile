FROM ubuntu:19.10

ENV DEBIAN_FRONTEND noninteractive

# System dependencies
RUN apt-get update \
 && apt-get install -y \
      curl \
      python3 \
      python3-pip \
      wget

# Install Node.js and npm. 
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
 && apt-get update \
 && apt-get install -y \
    nodejs \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install necessary libs to make the bundled version of Chromium that Puppeteer installs, work.
# From https://github.com/puppeteer/puppeteer/blob/master/docs/troubleshooting.md#running-puppeteer-in-docker
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
 && apt-get update \
 && apt-get install -y google-chrome-unstable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
      --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# Install Gunicorn as production WSGI server
RUN pip3 install gunicorn

# Copy package.json and package-lock.json and install Node.js deps.
# The install is done in /home as that is the parent dir
COPY package*.json /home/
RUN cd /home && npm install

# Create non-root user and home directory, because it is generally good practice,
# and in this case necessary for Encoda to be able to run Chromium without the
# unsafe `--no-sandbox` option.
RUN useradd -ms /bin/bash director
WORKDIR /home/director
USER director

# Copy requirements.txt and install Python deps.
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy over remaining files
ADD --chown=director:director . .

# Run `wsgi.py` using Gunicorn
CMD gunicorn wsgi --bind 0.0.0.0:8000
