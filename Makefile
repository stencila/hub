all: format lint test build run

# Format code for each service
format:
	make -C director format
	make -C overseer format
	make -C worker format

# Lint code for each service
lint:
	make -C director lint
	make -C overseer lint
	make -C worker lint

# Run unit tests for each service
test:
	make -C director test
	make -C worker test

# Run unit tests with coverage for each service
cover:
	make -C director cover
	make -C worker cover

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
