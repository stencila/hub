FROM python:3.7

# Create `monitor` user and use it's home dir
RUN useradd -m monitor
WORKDIR /home/monitor

# Install Python requirements
COPY requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python app files
COPY *.py ./

# Ensure Celery startup banner is printed
# See https://www.distributedpython.com/2018/10/01/celery-docker-startup/
ENV PYTHONUNBUFFERED=1

# Run Celery as the user `monitor`
# See https://stackoverflow.com/a/56383736 for reason for empty pidfile option
USER monitor
CMD python3 monitor.py
