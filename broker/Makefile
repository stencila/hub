# Build Docker image
build:
	docker build --tag stencila/hub-broker .

# Run Docker image
run: build
	docker run --rm --network=host \
		-e RABBITMQ_DEFAULT_PASS=password \
		stencila/hub-broker
