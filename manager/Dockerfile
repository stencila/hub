FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# System dependencies
RUN apt-get update \
 && apt-get install -y \
      curl \
      python3 \
      python3-pip \
      wget

# Install Gunicorn as production WSGI server
RUN pip3 install gunicorn

# Create non-root user and home directory, because it is generally good practice.
RUN useradd -ms /bin/bash manager
WORKDIR /home/manager
USER manager

# Add to PATH to prevent pip3 warning that installed
# packages are not on path.
ENV PATH="/home/manager/.local/bin:${PATH}"

# Copy requirements.txt and install Python deps.
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy over remaining files
ADD --chown=manager:manager . .

# Run `wsgi.py` using Gunicorn
CMD gunicorn manager.wsgi --bind 0.0.0.0:8000
