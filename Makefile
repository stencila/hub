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

build: router-build director-build

static: director-static

deploy: router-deploy director-deploy

release: router-deploy director-release

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
director/extern: package.json
	npm install
	
	mkdir -p $@/js/monaco-editor/min/vs
	cp -R node_modules/monaco-editor/min/vs/* $@/js/monaco-editor/min/vs/

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
# but using development database and static files.
# Add `-e DJANGO_CONFIGURATION="Dev"` to run in Dev mode instead.
director-rundocker: director-static
	$(EV) \
	docker run \
		-e DJANGO_SECURE_SSL_REDIRECT="False" \
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

push-tags:
	git push origin master
	git push --tags origin

tag-major:
	make increment-major
	make tag
	make push-tags

tag-minor:
	make increment-minor
	make tag
	make push-tags

tag-patch:
	make increment-patch
	make tag
	make push-tags
