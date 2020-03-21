# Shortcut to activate the virtual environment during development
VE := . venv/bin/activate ;

# Shortcut to set required environment variables during development
# Uses a custom `env.sh` or falls back to `env-example.sh`
EV := test -f ./env.sh && . ./env.sh || . ./env-example.sh ;

# Shortcut to run a Django manage.py task in the virtual environment
DJ ?= $(VE) $(EV) python3 manage.py

# Setup virtual environment
venv: requirements.txt
	python3 -m venv venv
	$(VE) pip3 install -r requirements.txt
	touch venv

# Setup DEV virtual environment
venv-dev: requirements.txt requirements-dev.txt
	python3 -m venv venv
	$(VE) pip3 install -r requirements.txt
	$(VE) pip3 install -r requirements-dev.txt
	touch venv

# Build any static files
# Needs `venv` to setup virtualenv for Django collectstatic
static: venv
	$(DJ) collectstatic --noinput

# Create migrations
migrations: venv
	$(DJ) makemigrations

# Build a development database
create-devdb: venv
	rm -f db.sqlite3
	$(DJ) migrate
	$(DJ) runscript create_dev_users
	$(DJ) runscript create_dev_accounts
	$(DJ) runscript create_dev_account_roles
	$(DJ) runscript create_dev_projects
	$(DJ) runscript create_dev_project_roles

# Migrate the development database
migrate-devdb: venv
	$(DJ) migrate

# Run development server
run: venv
	$(DJ) runserver

# Lint everything
lint: lint-code lint-types lint-docs
	
# Lint code
lint-code:
	$(VE) flake8 --exclude=venv,migrations,storage --max-line-length=120 .

# Lint types
lint-types:
	$(VE) mypy --config-file mypy.ini .

# Lint docs
lint-docs:
	$(VE) pydocstyle --match-dir='^(?!venv|\\.|migrations|tests|scripts|storage).*' .


# Run tests
test: venv
	$(VE) pytest

# Run tests with coverage
cover: venv
	$(VE) pytest --cov=. --cov-report term --cov-report html --cov-report xml

# Build Docker image
build: Dockerfile
	docker build --tag stencila/hub-director .

# Run the Docker image passing through
# environment variables required for `Prod` settings
# but using development database and static files.
# Add `-e DJANGO_CONFIGURATION="Dev"` to run in Dev mode instead.
run-docker: build static
	$(EV) \
	docker run \
		-e DJANGO_SECURE_SSL_REDIRECT="False" \
		-e DJANGO_SECRET_KEY \
		-e DJANGO_JWT_SECRET \
		-e DJANGO_BETA_TOKEN \
		-e DJANGO_SENDGRID_API_KEY \
		-v $$PWD/static:/home/director/static:ro \
		-v $$PWD/db.sqlite3:/home/director/db.sqlite3:rw \
		-v $$PWD/storage:/home/director/storage:rw \
		-v $$PWD/secrets:/home/director/secrets:ro \
		-p 8000:8000 -it --rm stencila/hub-director

clean:
	rm -rf venv coverage static
