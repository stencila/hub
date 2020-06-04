# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Shortcut to set required environment variables during development
# Exports the default values in ../.config && ../.secrets but
# with overrides for local development
EV := export $$(egrep -v '^\#' ../.config | xargs) ; \
      export $$(egrep -v '^\#' ../.secrets | xargs); \
	  export DEPLOYMENT_ENVIRONMENT=dev \
	         DATABASE_URL="sqlite:///dev.sqlite3" \
	         BROKER_URL="amqp://stencila:password@localhost:5672/stencila";

# Shortcut to run a Django manage.py task in the virtual environment
DJ ?= $(EV) $(VE)/python3 manage.py

# Python command to use for venv setup
PYTHON ?= python3

all: format lint test run

# Setup
# This exists just for consistency across projects;
# aliases to setting up the dev environment.
setup: venv

# Setup virtual environment, including both Python venv
# and node_modules
venv: requirements.txt  requirements-dev.txt package.json
	$(PYTHON) -m venv venv
	$(VE)/pip3 install -r requirements.txt
	$(VE)/pip3 install -r requirements-dev.txt
	touch venv
	npm install

# Build any static files
# Needs `venv` to setup virtualenv for Django collectstatic
# Uses Prod settings to avoid collecting static assets from
# packages not used in production e.g debug-toolbar
static: venv
	export DJANGO_CONFIGURATION="Prod"; $(DJ) collectstatic --noinput
.PHONY: static

# Create migrations
migrations: venv
	$(DJ) makemigrations

# Create a development SQLite database
create-devdb-sqlite: venv
	rm -f dev.sqlite3
	$(DJ) migrate
	$(DJ) runscript create_dev_db

# Migrate the development database
migrate-devdb: venv
	$(DJ) migrate

# Show model serializers
show-serializers:
	$(DJ) runscript show_serializers

# Run development server
run: venv
	$(DJ) runserver

# Run static asset compilation and live-reload server
run-watch:
	npm run start

# Run development server with production settings
run-prod: venv
	export DJANGO_CONFIGURATION="Prod"; \
	$(DJ) runserver

# Format code
format: venv
	$(VE)/black --exclude migrations .
	$(VE)/isort --apply

# Lint everything
lint: lint-format lint-code lint-types lint-docs

# Lint code formatting
lint-format: venv
	$(VE)/black --exclude migrations --check .
	$(VE)/isort --check-only
	npm run lint:format

# Lint code
lint-code: venv
	$(VE)/flake8

# Lint types
lint-types: venv
	$(VE)/mypy .

# Lint docs
lint-docs: venv
	$(VE)/pydocstyle

# Run tests
test: venv
	$(VE)/pytest

# Rerun tests when files change
test-watch: venv
	$(VE)/ptw

# Run tests with coverage and migrations
cover: venv
	$(VE)/pytest --cov=. --cov-report term --cov-report html --cov-report xml --migrations

# Create page snapshots
snaps: venv
	$(DJ) runscript create_page_snaps
.PHONY: snaps

# Build Docker image
build: Dockerfile
	docker build --tag stencila/hub-director .

clean:
	rm -rf venv coverage static
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
