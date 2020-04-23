# Build Docker image
build:
	docker build --tag stencila/hub-broker .

# Run Docker image
run: build
	cd .. && docker-compose run --rm broker
