FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# Install system dependencies
RUN apt-get update \
 && apt-get install -y \
        curl \
        python3 \
        python3-pip

# Install Node.js and npm. 
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - \
 && apt-get update \
 && apt-get install -y \
        nodejs \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install necessary libs for Encoda
# See https://github.com/stencila/encoda/blob/master/Dockerfile
RUN apt-get update \
 && apt-get install -y \
      libasound2 \
      libatk-bridge2.0-0 \
      libatk1.0-0 \
      libcups2 \
      libgbm1 \
      libgconf-2-4 \
      libgtk-3-0 \
      libgtk2.0-0 \
      libnotify-dev \
      libnss3 \
      libpangocairo-1.0-0 \
      libxcomposite1 \
      libxrandr2 \
      libxss1 \
      libxtst6 \
      xauth \
      xvfb \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Create non-root `worker` user and use it's home dir
# to copy files into
RUN useradd --create-home worker
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

# Run as non-root user
USER worker

# Use the array form of CMD to ensure that the celery process has PID 1
# so that it will receive SIGTERM for graceful shutdown
CMD ["celery", "--app=worker", "worker", "--heartbeat-interval=60"]
