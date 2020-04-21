# Build Docker image
build:
	docker build --tag stencila/hub-router .

# Run Docker image with necessary environment variables
run: build
	docker run -it --rm -p 9000:80 \
	  -e DIRECTOR_URL=http://127.0.0.1:8000 \
	  -e BROKER_URL=not-a-url-see-note-in-nginx.conf \
	  stencila/hub-router
