all: format lint test build run

# Format code for each service
format:
	make -C director format
	make -C overseer format

# Lint code for each service
lint:
	make -C director lint
	make -C overseer lint

# Run unit tests for each service
test:
	make -C director test

# Run unit tests with coverage for each service
cover:
	make -C director cover

# Build all images for all services
build:
	docker-compose build

# Run all services on localhost
run:
	docker-compose up

# Run in a Minikube cluster
run-in-minikube:
	eval $$(minikube docker-env) && docker-compose build
	kompose up
