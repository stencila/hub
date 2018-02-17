SHELL := bash
IMAGE := stencila-director
all: setup run

setup: director-setup director-env

run: director-run

docker: Dockerfile
	docker build -t $(IMAGE) .

deploy: docker
	docker tag $(IMAGE) stencila/hub
	docker push stencila/hub

DOCKER ?= docker run -e DJANGO_JWT_SECRET=$${DJANGO_JWT_SECRET} --net=host -it --rm -u $$(id -u):$$(id -g) -v $$(pwd):/work -w /work $(IMAGE)

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

# Build stencila
director/stencila/dist/stencila.js: 
	docker run --rm -v $$(pwd):/work -w /work/director/stencila node make setup build
director-stencila: director/stencila/dist/stencila.js
	cp -rv director/stencila/dist/{font-awesome,katex,lib,stencila.css*,stencila.js*} director/client/


# Build any static files
director-static: #director-stencila
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
