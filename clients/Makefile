THIS_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Create API Schema file api.yaml
api.yaml:
	../manager/venv/bin/python3 ../manager/manage.py runscript get_api_schema --script-args $@
	sed -i -e 's|host: testserver|host: hub.stenci.la|' $@
	sed -i -e 's|  - http|  - https|' $@

# Get help on client generation options
help:
	docker run openapitools/openapi-generator-cli help generate

# Get help on options for Python client generation
python-help:
	docker run openapitools/openapi-generator-cli config-help -g python

# Generate Python client
python: api.yaml
	docker run --rm -v "$(THIS_DIR):/work" -w /work -u $$(id -u):$$(id -g) openapitools/openapi-generator-cli generate \
	  -i api.yaml \
	  -c python/.openapi-generator-config.yaml \
	  -g python \
	  -o python
.PHONY: python

# Publish Python package to PyPI
# The following Twine command is intended to work on Azure Pipelines CI
# See https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/package/twine-authenticate
python-publish:
	pip3 install twine wheel
	cd python && \
	  python3 setup.py sdist bdist_wheel && \
	  python3 -m twine upload -r PyPI --config-file $(PYPIRC_PATH) dist/*

# Get help on options for Typescript client generation
typescript-help:
	docker run openapitools/openapi-generator-cli config-help -g typescript-fetch

# Generate Typescript client
typescript: api.yaml
	docker run --rm -v "$(THIS_DIR):/work" -w /work -u $$(id -u):$$(id -g) openapitools/openapi-generator-cli generate \
	  -i api.yaml \
	  -c typescript/.openapi-generator-config.yaml \
	  -g typescript-fetch \
	  -o typescript
.PHONY: typescript

# Publish Typescript package to PyPI
typescript-publish:
ifneq ("$(NPM_TOKEN)", "")
	echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > typescript/.npmrc
else
	@echo "Missing NPM_TOKEN env var"
	@exit 1
endif
	cd typescript && \
	  npm install && \
	  npm publish
