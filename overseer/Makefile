# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Python command to use for venv setup
PYTHON ?= python3

# Build virtual environment
venv: requirements.txt requirements-dev.txt
	$(PYTHON) -m venv venv
	$(VE)/pip3 install -r requirements.txt
	$(VE)/pip3 install -r requirements-dev.txt
	touch venv

# Format code
format: venv
	$(VE)/black .

# Lint code
lint: venv
	$(VE)/black --check .
	$(VE)/flake8
	$(VE)/mypy --config-file pyproject.toml .
	$(VE)/pydocstyle --match-dir='^(?!venv)'

# Run `overseer.py` during development to check configuration.
run: venv
	BROKER_URL=amqp://stencila:password@localhost:5672/stencila \
	DIRECTOR_URL=http://staff:staff@localhost:8000 \
	$(VE)/python3 overseer.py

# Run `celery flower` during development.
flower: venv
	$(VE)/celery flower --broker=amqp://stencila:password@localhost:5672/stencila

# Build Docker image
build:
	docker build --tag stencila/hub-overseer .

# Clean up venv and cached files
clean:
	rm -rf venv
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
