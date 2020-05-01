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
