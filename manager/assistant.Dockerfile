FROM python:3.9.6

# Create non-root `assistant` user and use it's home dir
# to copy files into
RUN useradd -m assistant
WORKDIR /home/assistant

# Copy requirements.txt and install Python deps.
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy over remaining files
ADD --chown=assistant:assistant . .

# Run non-root user
USER assistant

# Run Celery worker
# Use the array form of CMD to ensure that the celery process has PID 1
# so that it will receive SIGTERM for graceful shutdown
CMD ["celery", "--app=manager.assistant", "--loglevel=info", "worker"]
