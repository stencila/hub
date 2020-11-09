# Build Docker image
build:
	docker build --tag stencila/hub-database .

# Run Docker image
run: build
	docker run --rm \
		-e POSTGRES_PASSWORD=password \
		-p 5432:5432 \
		stencila/hub-database
