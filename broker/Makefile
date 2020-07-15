# Build Docker image
build:
	docker build --tag stencila/hub-broker .

# Run Docker image
run: build
	docker run --rm \
      	-p 5672:5672 \
      	-p 15672:15672 \
		-p 15692:15692 \
		-e RABBITMQ_DEFAULT_PASS=password \
		stencila/hub-broker
