# Build Docker image
build:
	docker build --tag stencila/hub-monitor .

# Run Docker image
run: build
	docker run --rm --network=host stencila/hub-monitor
