# Shortcut to refer to programs in the virtual environment during development
VE := venv/bin

# Build virtual environment
venv: requirements.txt
	python3 -m venv venv
	$(VE)/pip3 install -r requirements.txt
	touch venv

# Run `celery beat` during development to check configuration.
run: venv
	BROKER_URL=redis://localhost:6379/0 \
	DATABASE_URL=postgres://stencila:password@localhost:5432/hub \
	$(VE)/celery beat --app scheduler --loglevel debug

# Build Docker image
build:
	docker build --tag stencila/hub-scheduler .

# Clean up venv and cached files
clean:
	rm -rf venv
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
