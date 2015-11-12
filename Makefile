# Stencila hub Makefile

# Use bash, rather than sh, as shell
SHELL := /bin/bash


####################################################################################
# Director

# Shortcut to activate the virtual environment; used below
VE := . director/env/bin/activate ;
# Shortcut to run a Django manage.py task in the virtual environment; used below
DJ := $(VE) director/manage.py 

# Install server side Python libraries into virtual environment
director-env-build: director/pip-requirements.txt
	virtualenv director/env --python=/usr/bin/python2.7 --system-site-packages
	$(VE) pip install -r director/pip-requirements.txt

# Remove server virtual environment
director-env-clean:
	rm -rf director/env

# Clean out pyc files
director-pyc-clean:
	find director -name '*.pyc' -delete

# Run makemigrations
director-makemigrations:
	$(DJ) makemigrations

# Run migrations
# If there is an sqlite database created ensure it has
# the correct permissions
director-migrate:
	$(DJ) migrate
	if [ -e director/db.sqlite3 ]; then chmod 775 director/db.sqlite3 ; fi

# Collect static files
director-collectstatic:
	$(DJ) collectstatic --noinput

# Run shell
director-shell:
	$(DJ) shell

# Run tests for an app
# e.g. director-test-users
director-test-%:
	$(DJ) test $(word 3,$(subst -, ,$@))

# Run all tests
director-test:
	$(DJ) test

# Build director
director-build: director-env-build director-pyc-clean director-migrate director-collectstatic

# Run development server
director-runserver:
	$(DJ) runserver


# Sym link nginx configuration file
# Instead of symlinking, these files could be copied to their respective locations.
# But symlinking has the advantage that this only needs to be done once, not everytime that those configuration files change

/etc/nginx/sites-enabled/stencila-director.conf:
	sudo ln -sfT /srv/stencila/hub/director/nginx.conf /etc/nginx/sites-enabled/stencila-director.conf

# Copy in supervisord conf
/etc/supervisor/conf.d/stencila-director.conf: /srv/stencila/hub/director/supervisord.conf
	sudo ln -sfT /srv/stencila/hub/director/supervisord.conf /etc/supervisor/conf.d/stencila-director.conf

# Create logs directory
/srv/stencila/hub/director/logs:
	mkdir -p $@

director-serve-config: /etc/nginx/sites-enabled/stencila-director.conf \
			           /etc/supervisor/conf.d/stencila-director.conf \
			           /srv/stencila/hub/director/logs

# Start servers
director-serve-start: director-serve-config
	sudo service supervisor start
	sudo service nginx start

# Stop servers
director-serve-stop: director-serve-config
	sudo service supervisor stop
	sudo service nginx stop

# Restart servers. Note that supervisor does not "restart" from stopped state.
director-serve-restart: director-serve-config
	if pgrep supervisord > /dev/null;\
		then sudo service supervisor stop ;\
		while pgrep supervisord;\
			do echo "waiting for supervisor to stop";\
			sleep 1;\
		done;\
	fi
	sudo service supervisor start
	sudo service nginx restart


##########################################################################
# Curator

# Build virtualenv for curator locally
curator-build:
	cd curator ;\
		. env/bin/activate ;\
			pip install -r pip-requirements.txt

# Run curator.py during development
# For testing with requests the Chrome app "Postman" (or similar) is recommended as it
# shows the friendly HTML debugger
curator-py-develop:
	cd curator ;\
		if [ ! -e env ] ;\
			then virtualenv env ;\
		fi ;\
		. env/bin/activate ;\
			pip install -r pip-requirements.txt ;\
			python curator.py 'dev'

# Run curator.go during development
curator-go-develop:
	cd curator ;\
		go run curator.go

# Test locally
curator-test:
	cd curator ;\
		. env/bin/activate ;\
			python tests.py
