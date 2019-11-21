SHELL := bash
OS := $(shell uname -s)
DIRECTOR_VERSION := $(shell ./version-get.sh)
GIT_BRANCH := $(shell git branch | grep \* | cut -d ' ' -f2)
VENV_DIR := venv

all: setup run

setup: director-venv

run: director-run

lint: director-lint

test: director-test

build: router-build director-build desktop-build

static: director-static desktop-static

deploy: router-deploy director-deploy desktop-deploy

release: router-deploy director-release desktop-deploy

# Exit with status 1 if git has uncommitted changes.
git-dirty-check:
ifneq ($(GIT_BRANCH),master)
	@echo "Not on master branch, can't continue."
	@false
else
	git diff-index --quiet --cached HEAD -- && git diff-files --quiet --ignore-submodules --
endif


####################################################################################
# Router

# Build Docker image
router-build: router/Dockerfile
	docker build --tag stencila/hub-router router

# Run Docker image
router-rundocker: router-build
	docker run -it --rm --net=host \
	           -v $$PWD/router/nginx.conf:/etc/nginx/conf.d/default.conf:ro stencila/hub-router

# Push Docker image to Docker hub
router-deploy: router-build
	docker push stencila/hub-router


####################################################################################
# Director

# Shortcut to activate the virtual environment during development
VE := . $(VENV_DIR)/bin/activate ;

# Shortcut to set required environment variables during development
# Uses a custom `env.sh` or falls back to `env-example.sh`
EV := test -f director/env.sh && source director/env.sh || source director/env-example.sh ;

# Shortcut to run a Django manage.py task in the virtual environment; used below
DJ ?= $(VE) $(EV) python3 director/manage.py

# Setup virtual environment
.PHONY: $(VENV_DIR)
$(VENV_DIR): director/requirements.txt
	python3 -m venv $(VENV_DIR)
	$(VE) pip3 install -r director/requirements.txt
	touch $(VENV_DIR)
.PHONY: director-venv
director-venv: $(VENV_DIR)

# Setup DEV virtual environment
.PHONY: director-venv-dev
director-venv-dev:
	python3 -m venv $(VENV_DIR)
	$(VE) pip3 install -r director/requirements.txt
	$(VE) pip3 install -r director/requirements-dev.txt
	touch $(VENV_DIR)

# Build directory of external third party JS and CSS
director/extern: director/package.json
	cd director && npm install
	mkdir -p $@/js
	cp director/node_modules/vue/dist/vue.min.js $@/js
	cp director/node_modules/vue-upload-component/dist/vue-upload-component.min.js $@/js
	cp director/node_modules/moment/min/moment.min.js $@/js
	cp director/node_modules/vue-resource/dist/vue-resource.min.js $@/js
	cp director/node_modules/buefy/dist/buefy.min.js $@/js/buefy.min.js
	cp director/node_modules/@stencila/executa/dist/browser/index.js $@/js/executa-index.js
	mkdir -p $@/js/monaco-editor/min/vs
	cp -R director/node_modules/monaco-editor/min/vs/* $@/js/monaco-editor/min/vs/

	cp -R director/node_modules/@stencila/components/dist/stencila-components/ $@/stencila-components/

	mkdir -p $@/css
	cp director/node_modules/buefy/dist/buefy.min.css $@/css
	cp director/node_modules/bulma-switch/dist/css/bulma-switch.min.css $@/css
	touch $@

# Create UML models
director-models: $(VENV_DIR)
	$(DJ) graph_models -a -o director/models.png

# Build any static files
# Needs `$(VENV_DIR)` to setup virtualenv for Django collectstatic
director-static: $(VENV_DIR) director/extern
	$(DJ) collectstatic --noinput

# Create migrations
director-migrations: $(VENV_DIR)
	$(DJ) makemigrations

# Build a development database
director-create-devdb: $(VENV_DIR)
	rm -f director/db.sqlite3
	$(DJ) migrate
	$(DJ) runscript create_dev_users
	$(DJ) runscript create_dev_accounts
	$(DJ) runscript create_dev_account_roles
	$(DJ) runscript create_dev_projects
	$(DJ) runscript create_dev_project_roles

# Build a development database
director-migrate-devdb: $(VENV_DIR)
	$(DJ) migrate

# Run development server
director-run: $(VENV_DIR) director/extern
	$(DJ) runserver

# Run development server with production settings
director-runprod: $(VENV_DIR) director/extern
	$(EV) \
	export DJANGO_CONFIGURATION=Prod; \
	$(DJ) runserver


# Lint everything
director-lint: director-lint-code director-lint-types director-lint-docs
	
# Lint code
director-lint-code:
	$(VE) flake8 --exclude=venv,migrations,director/node_modules,director/storage --max-line-length=120 director

# Lint types
director-lint-types:
	$(VE) mypy --config-file director/mypy.ini director

# Lint docs
director-lint-docs:
	$(VE) pydocstyle --match-dir='^(?!venv|node_modules|\\.|migrations|tests|scripts|storage).*' director

# Run tests
director-test: $(VENV_DIR)
	$(DJ) test director


# Build Docker image
director-build: director/Dockerfile
	docker build --tag stencila/hub-director director

# Build Docker image with current version tag
director-docker-versioned-build: git-dirty-check director/Dockerfile
	docker build --tag stencila/hub-director:$(DIRECTOR_VERSION) director

# Run the Docker image passing through
# environment variables required for `Prod` settings
# but using development database and static files
director-rundocker: director-static
	$(EV) \
	docker run \
		-e DJANGO_SECRET_KEY \
		-e DJANGO_JWT_SECRET \
		-e DJANGO_BETA_TOKEN \
		-e DJANGO_SENDGRID_API_KEY \
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

# Push versioned Docker image to Docker hub
director-release: director-docker-versioned-build
	docker push stencila/hub-director:$(DIRECTOR_VERSION)

# Increment the Major Version of director
increment-major: git-dirty-check
	./version-increment.sh major

# Increment the Minor Version of director
increment-minor: git-dirty-check
	./version-increment.sh minor

# Increment the Patch Version of director
increment-patch: git-dirty-check
	./version-increment.sh patch

# Make annotated tag based on the director version
tag: git-dirty-check
	git tag -a v$(DIRECTOR_VERSION) -m "Hub version $(DIRECTOR_VERSION)"


####################################################################################
# Desktop

# Setup locally
desktop/node_modules: desktop/package.json
	cd desktop && npm install
	touch $@
desktop-setup: desktop/node_modules

# Collect static files
desktop/node_modules/stencila/dist/:
	mkdir -p $@
desktop/static/dist/: desktop/node_modules desktop/node_modules/stencila/dist/
	mkdir -p $@
	rsync --verbose --archive --recursive --delete desktop/node_modules/stencila/dist/ $@
	touch $@
desktop-static: desktop-setup desktop/static/dist/

# Run locally
desktop-run: desktop-static
	cd desktop && JWT_SECRET='not-a-secret' npm start

# Build Docker image
# This copies static JS, CSS & HTML into the image to be served from there
desktop-build: desktop/Dockerfile desktop-static
	docker build --tag stencila/hub-desktop desktop

# Run Docker image
# This mounts the `desktop/dars` folder into the Docker container
desktop-rundocker: desktop-build
	docker run \
		-e JWT_SECRET='not-a-secret' \
		-it --rm -p 4000:4000 -v $$PWD/desktop/projects:/home/desktop/projects:rw stencila/hub-desktop

# Push Docker image to Docker hub
desktop-deploy: desktop-build
	docker push stencila/hub-desktop


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
