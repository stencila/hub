SHELL := bash

OS := $(shell uname -s)

all: setup run

setup: director-setup director-env

run: director-run

build: director-build

deploy: director-deploy

DOCKER ?= docker run -e DJANGO_JWT_SECRET=$${DJANGO_JWT_SECRET} --net=host -it --rm -u $$(id -u):$$(id -g) -v $$(pwd):/work -w /work stencila/hub-director

interact:
	$(DOCKER) bash


####################################################################################
# Director

# Shortcut to activate the virtual environment; used below
VE := . director/env/bin/activate ;

# Shortcut to run a Django manage.py task in the virtual environment; used below
ifeq ($(DOCKER),false)
	DJ ?= $(VE) python3 director/manage.py
else
	DJ ?= $(DOCKER) python3 director/manage.py 
endif

# Install necessary system packages
director-setup:
ifeq ($(OS),Linux)
	sudo apt-get install libev-dev
endif
ifeq ($(OS),Darwin)
	brew install libev
endif

# Setup virtual environment
director-env: director/requirements.txt
	python3 -m venv director/env
	$(VE) pip3 install wheel
	$(VE) pip3 install -r director/requirements.txt

# Build stencila/stencila Javascript and CSS
director/stencila/dist/stencila.js:
ifeq ($(DOCKER),false)
	cd director/stencila && make setup build
else
	docker run --rm -v $$(pwd):/work -w /work/director/stencila node make setup build
endif
director-stencila: director/stencila/dist/stencila.js
	mkdir -p director/client/stencila
	cp -rv director/stencila/dist/{font-awesome,katex,lib,stencila.css*,stencila.js*} director/client/stencila

# Build any static files
director-static: director-stencila
	$(DJ) collectstatic --noinput

# Build a development database
director-devdb:
	rm -f director/db.sqlite3
	rm -fr director/director/migrations
	$(DJ) makemigrations director
	$(DJ) migrate
	$(DJ) runscript create_allauth
	$(DJ) runscript create_users
	$(DJ) runscript create_projects

# Run development server
director-run: director-static
	$(DJ) runserver

# Run development server on http://stenci.la:80
# This is useful for testing allauth callbacks.
# You need to add a `127.0.0.1 stenci.la` line to 
# hosts file using `sudo nano /etc/hosts`
director-run80: director-static
	sudo director/env/bin/python3 director/manage.py runserver stenci.la:80

# Build director Docker image
director-build: director/Dockerfile
	docker build -t stencila/hub-director director

# Push director Docker image to Docker hub
director-deploy: director-build
	docker push stencila/hub-director
