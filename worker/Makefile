# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Build virtual environment
venv: requirements.txt
	python3 -m venv venv
	$(VE)/pip3 install -r requirements.txt
	touch venv

# Run `celery worker` during development to check configuration.
# Change env vars as needed for your dev env.
run: venv
	BROKER_URL=amqp://stencila:password@localhost:5672/stencila \
	$(VE)/celery worker --app worker --events --queues stencila --hostname worker@stencila

# Build Docker image
build:
	docker build --tag stencila/hub-worker .

# Clean up venv and cached files
clean:
	rm -rf venv
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
