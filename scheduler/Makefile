# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Python command to use for venv setup
PYTHON ?= python3

# Build virtual environment
venv: requirements.txt
	$(PYTHON) -m venv venv
	$(VE)/pip3 install -r requirements.txt
	touch venv

# Run `celery beat` during development to check configuration.
run: venv
	BROKER_URL="amqp://stencila:password@localhost:5672/stencila" \
	DATABASE_URL=postgres://stencila:password@localhost:5432/hub \
	$(VE)/celery --app scheduler --loglevel debug beat

# Build Docker image
build:
	docker build --tag stencila/hub-scheduler .

# Clean up venv and cached files
clean:
	rm -rf venv
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
