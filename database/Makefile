# Build Docker image
build:
	docker build --tag stencila/hub-database .

# Run Docker image
run: build
	cd .. && docker-compose run --rm database
