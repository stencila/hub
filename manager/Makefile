# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Shortcut to set required environment variables during development
# Exports the default values in ../.config && ../.secrets but
# with overrides for local development
EV := export $$(egrep -v '^\#' ../.config | xargs) ; \
      export $$(egrep -v '^\#' ../.secrets | xargs); \
	  export DEPLOYMENT_ENVIRONMENT=dev \
	         DJANGO_CONFIGURATION=Dev \
			 DATABASE_URL="sqlite:///dev.sqlite3" \
	         BROKER_URL="amqp://stencila:password@localhost:5672/stencila" \
			 CACHE_URL="redis://stencila:password@localhost:6379/0";

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
	$(VE)/pip3 install wheel
	$(VE)/pip3 install -r requirements.txt
	$(VE)/pip3 install -r requirements-dev.txt
	touch venv
	npm install

# Build any static files
# Uses Prod settings to avoid collecting static assets from
# packages not used in production e.g debug-toolbar
static: venv
	npm run build
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

# Create a development PostgeSQL database on localhost
create-devdb-postgres: venv
	export DATABASE_URL="postgres://stencila:password@localhost:5432/hub"; \
	$(VE)/python3 manage.py reset_db; \
	$(VE)/python3 manage.py migrate; \
	$(VE)/python3 manage.py runscript create_dev_db

# Migrate the development database
migrate-devdb: venv
	$(DJ) migrate

# Show model serializers
show-serializers:
	$(DJ) runscript show_serializers

# Show all URLs
show-urls:
	$(DJ) show_urls

# Run development server
# Do not use multithreading as this can issues with SQLite
# if there is more than one thread attempting to write to
# the database.
run: venv
	$(DJ) runserver --nothreading

# Run development server with PostgreSQL database
run-postgres: venv
	$(EV) \
	export DATABASE_URL="postgres://stencila:password@localhost:5432/hub"; \
	$(VE)/python3 manage.py runserver

# Run static asset compilation and live-reload server
run-watch:
	npm run start

# Run development server with staging settings
run-staging: venv
	$(EV) \
	export DJANGO_CONFIGURATION="Staging"; \
	$(VE)/python3 manage.py runserver

# Run development server with production settings
run-prod: venv
	$(EV) \
	export DJANGO_CONFIGURATION="Prod"; \
	$(VE)/python3 manage.py runserver

# Format code
format: venv
	$(VE)/black --exclude migrations .
	$(VE)/isort .
	npm run lint:format

# Lint everything
lint: lint-format lint-code lint-types lint-docs

# Lint code formatting
lint-format: venv
	$(VE)/black --exclude migrations --check .
	$(VE)/isort . --check

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
# Tests require that static files are built because they
# do not use the development serving of static files, they
# use whitenoise served static files instead.
test: venv static
	$(VE)/pytest

# Rerun tests when files change
test-watch: venv static
	$(VE)/ptw

# Run tests with coverage
cover: venv static
	$(VE)/pytest --cov=. --cov-report term --cov-report html --cov-report xml

# Create page snapshots
# Requires that the development server be running on https://localhost:8000
snaps: venv
	$(DJ) runscript create_page_snaps
.PHONY: snaps

# Build Docker image
build: Dockerfile static
	docker build --tag stencila/hub-manager .

# Run Docker image
#
# This setup aims to be as close to production as possible without
# the need for secret variables.
# Add `--env DJANGO_CONFIGURATION="Dev"` to run in Dev mode instead.
# Necessary environment variables required for `Prod` settings need to
# be passed using the `--env` option.
# Uses development database and local storage directory.
# Uses `DJANGO_SECURE_SSL_REDIRECT=false` to avoid being redirected
# to HTTPS (which is the default for prod)
run-docker: build
	$(EV) \
	docker run \
		--env DJANGO_SECRET_KEY \
		--env DJANGO_SENDGRID_API_KEY \
		--env DJANGO_SECURE_SSL_REDIRECT=false \
		--env DJANGO_MEDIA_ROOT=/storage/media \
		--env DJANGO_UPLOADS_ROOT=/storage/uploads \
		--env DJANGO_WORKING_ROOT=/storage/working \
		--env DJANGO_SNAPSHOTS_ROOT=/storage/snapshots \
		-v $$PWD/../storage/data:/storage:rw \
		--env BROKER_URL \
		--env CACHE_URL \
		-v $$PWD/dev.sqlite3:/home/manager/dev.sqlite3:rw \
		-p 8000:8000 -it --rm stencila/hub-manager

clean:
	rm -rf venv coverage static
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
