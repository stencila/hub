# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Python command to use for venv setup
PYTHON ?= python3

# Build virtual environment (Python and Node packages)
venv: requirements.txt requirements-dev.txt package.json
	$(PYTHON) -m venv venv
	$(VE)/pip3 install -r requirements.txt
	$(VE)/pip3 install -r requirements-dev.txt
	touch venv
	npm install

# Format code
format: venv
	$(VE)/black .

# Lint code
lint: venv
	$(VE)/black --check .
	$(VE)/flake8
	$(VE)/mypy --config-file pyproject.toml .
	$(VE)/pydocstyle --match-dir='^(?!venv)'

# Run tests
test: venv
	$(VE)/pytest --ignore=node_modules --ignore venv --ignore projects

# Run tests with coverage
cover: venv
	$(VE)/pytest --ignore=node_modules  --ignore venv --ignore projects \
	             --cov=. --cov-report term --cov-report html --cov-report xml

# Run `celery worker` during development to check configuration.
# Falls back to using RPC result backend, add
# 	CACHE_URL=redis://stencila:password@localhost:6379/0
# to use Redis instead
# Uses timestamp to generate unique hostnames for workers.
# Uses prefetch-multiplier=1: "only reserve one task per worker process at a time". 
# See https://docs.celeryproject.org/en/stable/userguide/optimizing.html#prefetch-limits
QUEUES ?= default
run: venv
	BROKER_URL=amqp://stencila:password@localhost:5672/stencila \
	$(VE)/celery worker \
		--app worker \
		--hostname worker-$$(date +'%s')@%h \
		--queues $(QUEUES) \
		--concurrency=4 \
		--prefetch-multiplier=1 \
		--events \
		--heartbeat-interval=30 \
		--loglevel DEBUG

# Build Docker image
build:
	docker build --tag stencila/hub-worker .

# Run Docker image
run-docker: build
	docker run --rm -it --network=host \
		--env BROKER_URL=amqp://stencila:password@localhost:5672/stencila \
		--env CACHE_URL=redis://stencila:password@localhost:6379/0 \
		stencila/hub-worker

# Clean up venv and cached files
clean:
	rm -rf venv
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
