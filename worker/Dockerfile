FROM stencila/executa:20200414.1

# This is necessary because the executa image
# defaults to a guest user.
USER root

# Create `worker` user and use it's home dir
RUN useradd -m worker
WORKDIR /home/worker

# Install Python requirements
COPY requirements.txt ./  
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Python app files
COPY . ./

# Ensure Celery startup banner is printed
# See https://www.distributedpython.com/2018/10/01/celery-docker-startup/
ENV PYTHONUNBUFFERED=1

# Run Celery as the user `worker`
USER worker

# Register executors as `worker` so that they can be discovered by Executa
# It is necessary to do this again for the `worker` user because
# the executors are not yet smart enough to register themselves
# system wide when registered by a root user in the `FROM` image
# and because we are using a different user.
RUN basha register
RUN node /usr/lib/node_modules/@stencila/encoda/dist/encoda.js register
RUN python3 -m stencila.pyla register
RUN R -e 'rasta::register()'

CMD celery worker --app worker --events --queues stencila --hostname worker@stencila
