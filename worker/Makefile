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
	node install

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
	$(VE)/pytest

# Run tests with coverage
cover: venv
	$(VE)/pytest --cov=. --cov-report term --cov-report html --cov-report xml

# Run `celery worker` during development to check configuration.
# Change env vars as needed for your dev env.
run: venv
	BROKER_URL=amqp://stencila:password@localhost:5672/stencila \
	$(VE)/celery worker \
		--app worker \
		--hostname worker@zone \
		--queues default \
		--events \
		--heartbeat-interval 30 \
		--loglevel DEBUG

# Build Docker image
build:
	docker build --tag stencila/hub-worker .

# Run Docker image
run-docker: build
	docker run --rm --network=host \
		--env BROKER_URL=amqp://stencila:password@localhost:5672/stencila \
		stencila/hub-worker

# Clean up venv and cached files
clean:
	rm -rf venv
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
