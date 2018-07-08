SHELL := bash
OS := $(shell uname -s)


all: setup run

setup: director-setup director-env

run: director-run

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

# Install necessary system packages
director-setup: director-setup-dirs
	# Install necessary system dependencies etc
ifeq ($(OS),Linux)
	sudo apt-get install libev-dev
endif
ifeq ($(OS),Darwin)
	brew install libev
endif

director-setup-dirs:
	# Setup directories
	mkdir -p secrets
	ln -sfT ../secrets director/secrets
	mkdir -p storage
	ln -sfT ../storage director/storage

# Setup virtual environment
director/venv: director/requirements.txt
	python3 -m venv director/venv
	$(VE) pip3 install -r director/requirements.txt
	touch director/venv
director-venv: director/venv

# Build any static files
# Needs `director/venv` to setup virtualenv for Django collectstatic
director-static: director/venv director-stencila
	$(DJ) collectstatic --noinput

# Create migrations
director-migrations: director/venv
	$(DJ) makemigrations director

# Build a development database
director-devdb: director/venv
	rm -f director/db.sqlite3
	$(DJ) migrate
	$(DJ) runscript create_dev_users

# Run development server
director-run: director/venv
	$(DJ) runserver

# Build Docker image
director-build: director/Dockerfile
	docker build --tag stencila/hub-director director

# Run the Docker image passing through
# environment variables required for `Prod` settings
# but using development database
director-rundocker:
	$(EV) \
	docker run \
		-e DJANGO_SECRET_KEY='not-a-secret' \
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
