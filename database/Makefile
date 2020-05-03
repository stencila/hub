# Build Docker image
build:
	docker build --tag stencila/hub-database .

# Run Docker image
run: build
	docker run --rm --network=host \
		-e POSTGRES_PASSWORD=password \
		stencila/hub-database
