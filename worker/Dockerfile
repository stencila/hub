FROM python:3.7

# Create `worker` user and use it's home dir
RUN useradd -m worker
WORKDIR /home/worker

# Install Python requirements
COPY requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python app files
COPY *.py ./

# Ensure Celery startup banner is printed
# See https://www.distributedpython.com/2018/10/01/celery-docker-startup/
ENV PYTHONUNBUFFERED=1

# Run Celery as the user `worker`
USER worker
CMD celery worker --app worker --queues stencila --hostname worker@stencila
