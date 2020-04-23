# Build Docker image
build:
	docker build --tag stencila/hub-router .

# Run Docker image
run: build
	cd .. && docker-compose run -e DIRECTOR_URL=http://127.0.0.1:8000 --rm router
