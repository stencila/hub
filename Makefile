# Stencila hub Makefile

# Use bash, rather than sh, as shell
SHELL := /bin/bash


rundev-startup:
	sudo ip address add 10.0.1.25 dev lo
	sudo ip address add 10.0.1.50 dev lo
	sudo ip address add 10.0.1.100 dev lo

rundev-shutdown:
	sudo ip address delete 10.0.1.25/32 dev lo
	sudo ip address delete 10.0.1.50/32 dev lo
	sudo ip address delete 10.0.1.100/32 dev lo


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

# Sync cron jobs from django-crontab to the machine user's cron table
# `django-crontab` can complain if the hash for a job has changed (because it's spec has changed)
# So this does the brute force approach of simply removing any existing cron table!
director-crons:
	-crontab -r
	$(DJ) crontab add

# Build client side files
director-client-build:
	cd director/general; \
		npm install;

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
director-build: director-env-build director-pyc-clean director-migrate director-client-build director-collectstatic

# Run development server
# Needs:
#   - port 7300 because in local mode that is where the worker container attempts to git clone from
#   - threaded because a request to director can trigger another request to director via worker (e.g. via a git clone)
#     and if you don't have multiple threads it just waits for itself!
director-rundev:
	director/env/bin/python director/manage.py runserver_plus --threaded 0.0.0.0:7300

# Run development server on port 80
director-rundev-80:
	sudo director/env/bin/python director/manage.py runserver_plus 0.0.0.0:80

# Run development server with SSL on port 443
director-rundev-ssl:
	sudo director/env/bin/python director/manage.py runserver_plus --cert /tmp/cert 0.0.0.0:443



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
		if [ ! -e env ] ;\
			then virtualenv env ;\
		fi ;\
		. env/bin/activate ;\
			pip install pip==8.1.1 ;\
			pip install -r pip-requirements.txt

# Run curator.py during development
# For testing with requests the Chrome app "Postman" (or similar) is recommended as it
# shows the friendly HTML debugger
curator-py-rundev:
	$(MAKE) curator-build
	cd curator ;\
		env/bin/python curator.py 'dev'

# Run curator.go during development
curator-go-rundev:
	cd curator ;\
		go run curator.go

# Test locally
curator-test:
	cd curator ;\
		. env/bin/activate ;\
			python tests.py


##########################################################################
# Worker

# Run worker.py during development
# For testing with requests the Chrome app "Postman" (or similar) is recommended as it
# shows the friendly HTML debugger
worker-rundev:
	cd worker ;\
		if [ ! -e env ] ;\
			then virtualenv env ;\
		fi ;\
		. env/bin/activate ;\
			pip install -r pip-requirements.txt ;\
			python worker.py 'dev'
