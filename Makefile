SHELL := bash

all: setup run

setup: director-setup director-env

run: director-run

docker: director/Dockerfile
	docker build -t stencila/hub/director director

deploy: docker
	docker push stencila/hub/direcor

DOCKER ?= docker run -e DJANGO_JWT_SECRET=$${DJANGO_JWT_SECRET} --net=host -it --rm -u $$(id -u):$$(id -g) -v $$(pwd):/work -w /work stencila/hub/director

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

# Install necessary packages
director-setup:
	sudo apt-get install python3.6 python3.6-dev python3.6-venv libev-dev

# Setup virtual environment
director-env: director/requirements.txt
	python3 -m venv director/env
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

# Run development server
director-run: director-static
	$(DJ) runserver

sync-dev-db:
	rm -f director/db.sqlite3
	rm -fr director/director/migrations
	$(DJ) makemigrations director
	$(DJ) migrate
	$(DJ) loaddata users
	$(DJ) loaddata projects
	$(DJ) loaddata clusters
