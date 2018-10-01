SHELL := bash
OS := $(shell uname -s)


all: setup run

setup: director-venv

run: director-run

lint: director-lint

test: director-test

build: router-build director-build editor-build

static: director-static editor-static

deploy: router-deploy director-deploy editor-deploy


####################################################################################
# Router

# Build Docker image
router-build: router/Dockerfile
	docker build --tag stencila/hub-router router

# Run Docker image
router-rundocker:
	docker run -it --rm --net=host \
	           -v $$PWD/router/nginx.conf:/etc/nginx/conf.d/default.conf:ro stencila/hub-router

# Push Docker image to Docker hub
router-deploy: router-build
	docker push stencila/hub-router


####################################################################################
# Director

# Shortcut to activate the virtual environment during development
VE := . director/venv/bin/activate ;

# Shortcut to set required environment variables during development
# Uses a custom `env.sh` or falls back to `env-example.sh`
EV := test -f director/env.sh && source director/env.sh || source director/env-example.sh ;

# Shortcut to run a Django manage.py task in the virtual environment; used below
DJ ?= $(VE) $(EV) python3 director/manage.py



# Setup virtual environment
director/venv: director/requirements.txt director/requirements-dev.txt
	python3 -m venv director/venv
	$(VE) pip3 install -r director/requirements.txt
	$(VE) pip3 install -r director/requirements-dev.txt
	touch director/venv
director-venv: director/venv

# Build directory of external third party JS and CSS
director/extern: director/package.json
	cd director && npm install
	mkdir -p $@/js
	cp director/node_modules/vue/dist/vue.min.js $@/js
	cp director/node_modules/vue-upload-component/dist/vue-upload-component.min.js $@/js
	cp director/node_modules/moment/min/moment.min.js $@/js
	cp director/node_modules/vue-resource/dist/vue-resource.min.js $@/js
	cp director/node_modules/buefy/lib/index.js $@/js/buefy.min.js
	mkdir -p $@/css
	cp director/node_modules/buefy/lib/buefy.min.css $@/css
	touch $@

# Create UML models
director-models: director/venv
	$(DJ) graph_models -a -o director/models.png

# Build any static files
# Needs `director/venv` to setup virtualenv for Django collectstatic
director-static: director/venv director/extern
	$(DJ) collectstatic --noinput

# Create migrations
director-migrations: director/venv
	$(DJ) makemigrations

# Build a development database
director-create-devdb: director/venv
	rm -f director/db.sqlite3
	$(DJ) migrate
	$(DJ) runscript create_dev_users
	$(DJ) runscript create_dev_accounts
	$(DJ) runscript create_dev_account_roles
	$(DJ) runscript create_dev_projects
	$(DJ) runscript create_dev_project_roles

# Build a development database
director-migrate-devdb: director/venv
	$(DJ) migrate

# Run development server
director-run: director/venv director/extern
	$(DJ) runserver

# Run development server with production settings
director-runprod: director/venv director/extern
	$(EV) \
	export DJANGO_CONFIGURATION=Prod; \
	$(DJ) runserver


# Lint everything
director-lint: director-lint-code director-lint-types director-lint-docs
	
# Lint code
director-lint-code:
	$(VE) flake8 --exclude=venv,migrations --max-line-length=120 director

# Lint types
director-lint-types:
	$(VE) mypy --config-file director/mypy.ini director

# Lint docs
director-lint-docs:
	$(VE) pydocstyle --match-dir='^(?!venv|\\.).*' director


# Run tests
director-test: director/venv
	$(DJ) test


# Build Docker image
director-build: director/Dockerfile
	docker build --tag stencila/hub-director director

# Run the Docker image passing through
# environment variables required for `Prod` settings
# but using development database and static files
director-rundocker: director-static
	$(EV) \
	docker run \
		-e DJANGO_SECRET_KEY \
		-e DJANGO_JWT_SECRET \
		-e DJANGO_BETA_TOKEN \
		-e DJANGO_SENDGRID_API_KEY \
		-v $$PWD/director/static:/home/director/static:ro \
		-v $$PWD/director/db.sqlite3:/home/director/db.sqlite3:rw \
		-v $$PWD/storage:/home/director/storage:rw \
		-v $$PWD/secrets:/home/director/secrets:ro \
		-p 8000:8000 -it --rm stencila/hub-director

# Interact with the Docker image
director-interact:
	$(DOCKER_RUN) bash

# Push Docker image to Docker hub
director-deploy: director-build
	docker push stencila/hub-director


####################################################################################
# Editor

editor-setup:
	# Setup directories
	mkdir -p storage
	ln -sfT ../storage editor/storage

# Setup locally
editor/node_modules: editor/package.json
	cd editor && npm install
	touch $@

# Collect static files
editor-static: editor/node_modules
	mkdir -p editor/static/dist/
	rsync --verbose --archive --recursive --delete editor/node_modules/stencila/dist/ editor/static/dist/

# Run locally
editor-run: editor-static
	cd editor && npm start

# Build Docker image
editor-build: editor/Dockerfile editor-static
	docker build --tag stencila/hub-editor editor

# Run Docker image
editor-rundocker:
	docker run -it --rm -p 4000:4000 -v $$PWD/storage:/home/editor/storage:rw stencila/hub-editor

# Push Docker image to Docker hub
editor-deploy: editor-build
	docker push stencila/hub-editor


####################################################################################
# Secrets

secrets-encrypt:
	$(VE) python make.py encrypt_secret secrets/director-allauth.json
	$(VE) python make.py encrypt_secret secrets/director_dev_secrets.py
	$(VE) python make.py encrypt_secret secrets/stencila-general-test-serviceaccount.json

secrets-decrypt:
	$(VE) python make.py decrypt_secret secrets/director-allauth.json.enc
	$(VE) python make.py decrypt_secret secrets/director_dev_secrets.py.enc
	$(VE) python make.py decrypt_secret secrets/stencila-general-test-serviceaccount.json.enc
