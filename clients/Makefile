# Create API Schema file api.yaml
# Requires that the development server be running on https://localhost:8000
api.yaml:
	curl http://localhost:8000/api/schema > $@
	sed -i -e 's|host: localhost:8000|host: hub.stenci.la|' $@
	sed -i -e 's|  - http|  - https|' $@

# Get help on client generation options
help:
	docker run openapitools/openapi-generator-cli help generate

# Get help on options for Python client generation
python-help:
	docker run openapitools/openapi-generator-cli config-help -g python

# Generate Python client
python: api.yaml
	docker run --rm -v "${PWD}:/work" -w /work -u $$(id -u):$$(id -g) openapitools/openapi-generator-cli generate \
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
