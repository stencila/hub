SHELL := bash
OS := $(shell uname -s)


all: setup run

setup: director-setup director-env

run: director-run

build: director-build editor-build

static: director-static editor-static

deploy: director-deploy editor-deploy


####################################################################################
# Director

# Shortcut to activate the virtual environment; used below
VE := . director/env/bin/activate ;

# Shortcut to run a Django manage.py task in the virtual environment; used below
DJ ?= $(VE) python3 director/manage.py

# Install necessary system packages
director-setup:
ifeq ($(OS),Linux)
	sudo apt-get install libev-dev
	curl -L https://github.com/stencila/cli/releases/download/v0.29.3/stencila-linux-x64.tar.gz | tar xvz
	sudo mv stencila /usr/local/bin
endif
ifeq ($(OS),Darwin)
	brew install libev
endif

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

# Build a development database
director-devdb: director/env
	rm -f director/db.sqlite3
	rm -fr director/director/migrations
	$(DJ) makemigrations director
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

# Run the Docker image
director-rundocker:
	docker run \
		-e SECRET_KEY=not-a-secret \
		-e JWT_SECRET=not-a-secret \
		-e GS_PROJECT_ID=some-project-id \
		-e GS_CREDENTIALS=dome-creds \
		-e GS_BUCKET_NAME=a-name \
		-p 8080:8080 -it --rm stencila/hub-director

# Interact with the Docker image
director-interact:
	$(DOCKER_RUN) bash

# Push Docker image to Docker hub
director-deploy: director-build
	docker push stencila/hub-director


####################################################################################
# Editor

# Setup locally
editor/node_modules: editor/package.json
	cd editor && npm install
	touch $@

# Run locally
editor-run: editor/node_modules
	cd editor && npm start

# Collect static files
editor-static: editor/node_modules
	rm -rf editor/static
	mkdir -p editor/static
	cp editor/{index.html,editor.css,editor.js} editor/static/
	cp -r editor/node_modules/stencila/dist/ editor/static/

# Build Docker image
editor-build: editor/Dockerfile
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
