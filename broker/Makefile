# Build Docker image
build:
	docker build --tag stencila/hub-broker .

# Run Docker image
# Set hostname for Prometheus data persistence
# See https://github.com/docker-library/rabbitmq/issues/106#issuecomment-241882358
run: build
	docker run --rm --network=host \
		--hostname broker \
		-v $$PWD/data:/var/lib/rabbitmq \
		-e RABBITMQ_DEFAULT_PASS=password \
		stencila/hub-broker
