# Build Docker image
build:
	docker build --tag stencila/hub-broker .

# Run Docker image
run: build
	docker run -it --rm -p 6379:6379 stencila/hub-broker
