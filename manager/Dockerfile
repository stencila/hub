FROM python:3.9.6

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
# For for rationale for choice of options see:
#   https://pythonspeed.com/articles/gunicorn-in-docker/ and
#   https://docs.gunicorn.org/en/stable/design.html#how-many-workers
CMD gunicorn manager.wsgi \
      --worker-tmp-dir /dev/shm \
      --workers=3 \
      --threads=4 \
      --worker-class=gthread \
      --log-file=- \
      --bind 0.0.0.0:8000
