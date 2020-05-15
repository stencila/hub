# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Shortcut to set required environment variables during development
# Exports the default values in ../.config && ../.secrets but
# with overrides for local development
EV := export $$(egrep -v '^\#' ../.config | xargs) ; \
      export $$(egrep -v '^\#' ../.secrets | xargs); \
	  export DEPLOYMENT_ENVIRONMENT=dev export DATABASE_URL="sqlite:///dev.sqlite3";

# Shortcut to run a Django manage.py task in the virtual environment
DJ ?= $(EV) $(VE)/python3 manage.py

# Python command to use for venv setup
PYTHON ?= python3

all: setup run

# Setup
# This exists just for consistency across projects;
# aliases to setting up the dev environment.
setup: venv

# Setup virtual environment
venv: requirements.txt  requirements-dev.txt
	$(PYTHON) -m venv venv
	$(VE)/pip3 install -r requirements.txt
	$(VE)/pip3 install -r requirements-dev.txt
	touch venv

# Build any static files
# Needs `venv` to setup virtualenv for Django collectstatic
# Uses Prod to avoid collecting static assets from packages not used in production e.g debug-toolbar
static: venv
	export DJANGO_CONFIGURATION="Prod"; $(DJ) collectstatic --noinput
.PHONY: static

# Create migrations
migrations: venv
	$(DJ) makemigrations

# Create a development SQLite database
create-devdb-sqlite: venv
	$(DJ) reset_db; \
	$(DJ) migrate; \
	$(DJ) runscript create_devdb

# Create a development PostgeSQL database on localhost
create-devdb-pg: venv
	export DATABASE_URL="postgres://stencila:password@localhost:5432/hub"; \
	$(VE)/python3 manage.py reset_db; \
	$(VE)/python3 manage.py migrate; \
	$(VE)/python3 manage.py runscript create_devdb

# Migrate the development database
migrate-devdb: venv
	$(DJ) migrate

# Migrate the production database
# Setting the DJANGO_CONFIGURATION to prod is necessary
# to avoid attempting to import apps that are not available in prod e.g. debug toolbar
migrate-proddb:
    DJANGO_CONFIGURATION="Prod" python3 manage.py migrate

# Show model serializers
show-serializers:
	$(DJ) runscript show_serializers

# Run development server
run: venv
	$(DJ) runserver

# Run development server with production settings
# Required secrets will need to be set in `env.sh`
# Some env vars set to avoid polluting logs etc
run-prod: venv
	export DJANGO_CONFIGURATION="Prod"; \
	$(DJ) runserver

# Format code
format: venv
	$(VE)/black .

# Lint everything
lint: lint-format lint-code lint-types lint-docs

# Lint code formatting
lint-format: venv
	$(VE)/black --check .	
	
# Lint code
lint-code: venv
	$(VE)/flake8

# Lint types
lint-types: venv
	$(VE)/mypy --config-file mypy.ini .

# Lint docs
lint-docs: venv
	$(VE)/pydocstyle --match-dir='^(?!venv|\\.|migrations|tests|scripts|storage).*' .

# Run tests
test: venv
	$(VE)/pytest

# Rerun tests when files change
test-watch: venv
	$(VE)/ptw

# Run tests with coverage and migrations
cover: venv
	$(VE)/pytest --cov=. --cov-report term --cov-report html --cov-report xml --migrations

# Build Docker image
build: Dockerfile
	docker build --tag stencila/hub-director .

# Run the Docker image
# Necessary environment variables required for `Prod` settings need to
# be passed using the `--env` option.
# Add `-e DJANGO_CONFIGURATION="Dev"` to run in Dev mode instead.
# Uses development database.
# Uses `DJANGO_SECURE_SSL_REDIRECT=false` to avoid being redirected
# to HTTPS (which is the default for prod)
run-docker: build
	$(EV) \
	docker run \
		--env DJANGO_JWT_SECRET \
		--env DJANGO_SECRET_KEY \
		--env DJANGO_SECURE_SSL_REDIRECT=false \
		--env BROKER_URL \
		-v $$PWD/dev.sqlite3:/home/director/dev.sqlite3:rw \
		-p 8000:8000 -it --rm stencila/hub-director

clean:
	rm -rf venv coverage static
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
