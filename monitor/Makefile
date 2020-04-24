# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Build virtual environment
venv: requirements.txt requirements-dev.txt
	python3 -m venv venv
	$(VE)/pip3 install -r requirements.txt
	$(VE)/pip3 install -r requirements-dev.txt
	touch venv

# Run `monitor.py` during development to check configuration.
run: venv
	BROKER_URL=redis://localhost:6379/0 \
	DIRECTOR_URL=http://localhost:8000 \
	DIRECTOR_AUTH="user:user" \
	$(VE)/python3 monitor.py

# Run `celery flower` during development.
run-flower: venv
	$(VE)/celery flower --broker=redis://localhost:6379/0

# Build Docker image
build:
	docker build --tag stencila/hub-monitor .

# Clean up venv and cached files
clean:
	rm -rf venv
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
