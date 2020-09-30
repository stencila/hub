# Create API Schema file api.yaml
# Requires that the development server be running on https://localhost:8000
api.yaml:
	curl http://localhost:8000/api/schema > $@
	sed -i -e 's|host: localhost:8000|host: hub.stenci.la|' $@
	sed -i -e 's|  - http|  - https|' $@

# Get help on client generation options
help:
	docker run openapitools/openapi-generator-cli help generate

# Get help on client generation options for Python
python-help:
	docker run openapitools/openapi-generator-cli config-help -g python

# Generate Python client
python: api.yaml
	docker run --rm -v "${PWD}:/work" -w /work -u $$(id -u):$$(id -g) openapitools/openapi-generator-cli generate \
      -i api.yaml \
      --git-host github.com \
      --git-user-id stencila \
      --git-repo-id hub \
      --package-name stencila.hub \
	--template-dir python/templates \
      -g python \
      -o python
