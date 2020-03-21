# Build Docker image
build:
	docker build --tag stencila/hub-router .

# Run Docker image during development with
# config file mounted
run: build
	docker run -it --rm --net=host \
	           -v $$PWD/nginx.conf:/etc/nginx/conf.d/default.conf:ro stencila/hub-router
