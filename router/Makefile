# Build Docker image
build:
	docker build --tag stencila/hub-router .

# Run Docker image
# To test setting basic auth add
#     -e ROUTER_USER="tester"
#     -e ROUTER_PASSWORD="password"
run: build
	docker run --rm --network=host \
		-e MANAGER_HOST=localhost:8000 \
		-e MONITOR_URL=http://localhost:9090 \
		-e RESOLVER_ADDRESS=127.0.01 \
		stencila/hub-router
