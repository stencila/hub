FROM ubuntu:20.10

ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
 && apt-get install -y \
        curl \
        python3 \
        python3-pip

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
RUN curl -sL https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
 && apt-get update \
 && apt-get install -y --no-install-recommends\
        google-chrome-unstable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Create non-root `worker` user and use it's home dir
# to copy files into
RUN useradd -m worker
WORKDIR /home/worker

# Install Python dependencies
COPY requirements.txt ./  
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Node.js dependencies and add the binaries dir to PATH
COPY package*.json ./
RUN npm ci
ENV PATH="${PATH}:./node_modules/.bin"

# Copy worker files over (see .dockerignore for what is included)
COPY . ./

# Ensure Celery startup banner is printed
# See https://www.distributedpython.com/2018/10/01/celery-docker-startup/
ENV PYTHONUNBUFFERED=1

# Run Celery worker as `worker` user
USER worker
CMD celery worker --app worker --queues default --events --hostname worker@stencila
