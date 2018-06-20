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
VE := . director/env/bin/activate ;

# Shortcut to set required environment variables during development
# Uses a custom `env.sh` or falls back to `env-example.sh`
EV := (test -f director/env.sh && source director/env.sh) || source director/env-example.sh ;

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
	# Install Stencila Convert
	curl -L https://github.com/stencila/cli/releases/download/v0.29.4/stencila-linux-x64.tar.gz | tar xvz
	sudo mv stencila /usr/local/bin

director-setup-dirs:
	# Setup directories
	mkdir -p secrets
	ln -sfT ../secrets director/secrets
	mkdir -p storage
	ln -sfT ../storage director/storage

# Setup virtual environment
director/env: director/requirements.txt
	python3 -m venv director/env
	$(VE) pip3 install wheel
	$(VE) pip3 install -r director/requirements.txt
	touch director/env

# Build stencila/stencila Javascript and CSS
director-stencila:
	mkdir -p director/client/stencila
	# cp -rv director/stencila/dist/{font-awesome,katex,lib,stencila.css*,stencila.js*} director/client/stencila

# Build any static files
# Needs `director/env` to setup virtualenv for Django collectstatic
director-static: director/env director-stencila
	$(DJ) collectstatic --noinput

# Create migrations
director-migrations: director/env
	$(DJ) makemigrations director

# Build a development database
director-devdb: director/env
	rm -f director/db.sqlite3
	$(DJ) migrate
	$(DJ) runscript create_allauth
	$(DJ) runscript create_users
	$(DJ) runscript create_projects

# Run development server
director-run: director/env
	$(DJ) runserver

# Run development server on http://stenci.la:80
# This is useful for testing allauth callbacks.
# You need to add a `127.0.0.1 stenci.la` line to 
# hosts file using `sudo nano /etc/hosts`
director-run80: director-static
	sudo director/env/bin/python3 director/manage.py runserver stenci.la:80

# Build Docker image
director-build: director/Dockerfile
	docker build --tag stencila/hub-director director

# Run the Docker image passing through development
# environment variables
director-rundocker:
	$(EV) \
	docker run \
		-e DJANGO_SECRET_KEY \
		-e DJANGO_JWT_SECRET \
		-e DJANGO_GS_PROJECT_ID \
		-e DJANGO_GS_BUCKET_NAME \
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
