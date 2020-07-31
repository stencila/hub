# Build Docker image
build:
	docker build --tag stencila/hub-cache .

# Run Docker image
run: build
	docker run --rm \
      	-p 6379:6379 \
		-e REDIS_PASSWORD=password \
		stencila/hub-cache
