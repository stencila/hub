all: setup run

setup: director-setup

run: director-run

####################################################################################
# Director

# Shortcut to activate the virtual environment; used below
VE := . director/env/bin/activate ;

# Shortcut to run a Django manage.py task in the virtual environment; used below
DJ := $(VE) director/manage.py

# Install necessary packages
director-setup:
	sudo apt-get install python3.6 python3.6-dev python3.6-venv libev-dev
	git submodule init && git submodule update

# Setup virtual environment
director-env: director/requirements.txt
	python3 -m venv director/env
	$(VE) pip3 install -r director/requirements.txt

# Build styles
director/style/css/stencila.min.css: $(wildcard director/style/sass/*.sass)
	cd director/style && npm install && npm run build

# Build any static files
director-static: director/style/css/stencila.min.css

# Run development server
director-run: director-env director-static
	director/env/bin/python director/manage.py runserver
