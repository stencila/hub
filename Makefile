IMAGE := stencila-director
all: setup run

setup: director-setup

run: director-run

docker: Dockerfile
	docker build -t $(IMAGE) .

DOCKER ?= docker run --net=host -it --rm -u $$(id -u):$$(id -g) -v $$(pwd):/work -w /work $(IMAGE)

interact:
	$(DOCKER) bash

####################################################################################
# Director

# Shortcut to activate the virtual environment; used below
VE := . director/env/bin/activate ;

# Shortcut to run a Django manage.py task in the virtual environment; used below
DJ := $(VE) director/manage.py

# Install necessary packages
director-setup:
	sudo apt-get install python3.6 python3.6-dev python3.6-venv libev-dev

# Setup virtual environment
director-env: director/requirements.txt
	python3 -m venv director/env
	$(VE) pip3 install -r director/requirements.txt

# Build any static files
director-static:
	$(DJ) collectstatic --noinput

# Run development server
director-run: director-env director-static
	director/env/bin/python director/manage.py runserver

docker-run: director-static
	$(DOCKER) python3 director/manage.py runserver

sync-dev-db:
	rm -f director/db.sqlite3
	rm -fr director/director/migrations
	$(DJ) makemigrations director
	$(DJ) migrate
	$(DJ) loaddata users
	$(DJ) loaddata projects
	$(DJ) loaddata clusters
