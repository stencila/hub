<div align="center">
	<img src="http://stenci.la/img/logo-name.png" alt="Stencila" style="max-width:150px">
</div>
<br>

[![Build Status](https://dev.azure.com/stencila/stencila/_apis/build/status/stencila.hub?branchName=master)](https://dev.azure.com/stencila/stencila/_build/latest?definitionId=5&branchName=master)
[![Coverage](https://codecov.io/gh/stencila/hub/branch/master/graph/badge.svg)](https://codecov.io/gh/stencila/hub)
[![License](https://img.shields.io/badge/License-Apache%202.0-3262eb.svg)](https://opensource.org/licenses/Apache-2.0)

Stencila is an open source platform for authoring, collaborating on, and sharing data driven documents. This is the 
repository for the Stencila Hub. The Hub is the gateway to using Stencila on the web. It allows users to access the full 
functionality of Stencila without having to configure anything on their local machines.


## Features

A brief overview of features implemented by the Stencila Hub. These are current features, more are planned as we are 
under active development (specific features are labelled with the Future Feature Unicorn 🦄).

We also welcome your suggestions or code contributions for feature you'd like to see.

### Authentication

- Store user credentials securely inside the Hub database, or
- Authenticate with third party services such as Github, Google, Twitter and Orcid

### Projects

- Create Projects
    - Upload, manage and edit files and data in the browser (with [Monaco Editor](https://microsoft.github.io/monaco-editor/index.html))
- Link Remote Sources (Github, Google Drive 🦄 and Dropbox 🦄)
    - Seamlessly integrate all code and data no matter the source
- Allow Projects to be publicly accessible (or added to the Project Gallery 🦄)

### User Management

- Build Teams of Users
- Assign access to Projects at a User or Team level
- Fine-grained permissions to limit reading, writing, creation, etc per User or Team

### Sessions

- Start execution Sessions on Stencila Cloud
- Apply resource limits to execution contexts on a per Project basis
- Allow public or controlled access to execution sessions with a Token or Key
- Limit the number of concurrent Sessions or the total number of Sessions that have been spawned


## Implementation

Stencila Hub is implemented using [Django](https://www.djangoproject.com/), [Node.js](https://nodejs.org/en/), 
[Nginx](http://nginx.org/) and Docker (with the latter two being crucial for the Hub to cooperate with Stencila Cloud).

The projects in Stencila Hub can be created  by adding files from multiple sources and in multiple formats. The 
conversion between the formats is achieved by using 
[Stencila Encoda](https://github.com/stencila/encoda) which can be used as an independent command line tool ([Stencila CLI](https://github.com/stencila/stencila)).

The interactive code cells in the documents and sheets in Stencila Hub projects can be executed thanks to 
[Stencila Cloud](https://github.com/stencila/cloud) where hosts for execution contexts sit in Docker containers on a 
Kubernetes Cluster.

## Develop

### Services

Stencila Hub consists of several services each with it's own sub-folder. The README file for each service provides further details on the service, including its purpose, the current and potential alternative technical approaches, and tips for development:

* [`router`](router): A [Nginx](https://nginx.org/) server that routes requests to other services.
* [`director`](director): A [Django](https://www.djangoproject.com/) project containing most of the application logic.
* [`broker`](broker): A [RabbitMQ](https://www.rabbitmq.com/) instance that acts as a message queue broker.
* [`worker`](worker): Celery `worker` processes that run jobs from the `broker`'s queue.
* [`scheduler`](scheduler): A [Celery](https://docs.celeryproject.org) `beat` process that schedules jobs to the `broker`'s queue.
* [`overseer`](overseer): A Celery process which monitors events associated with workers and job queues.
* [`cache`](cache): 🦄 A [Redis](https://redis.io) instance that acts as a cache for Django.
* [`storage`](storage): 🦄 A S3-compatible [Minio](https://min.io) object store used by several other services.
* [`database`](database): A [PostgreSQL](https://www.postgresql.org/) database used by the `director`.

### Getting started

The folder for each service contains a `Makefile` which has a `run` recipe for running the service during development e.g.

```sh
make -C director run
```

These `run` recipes are useful for quickly iterating during development and, in the case of the `director`, will hot-reload when source files are edited. Where possible, the `run` recipes will use a local Python virtual environment. In other cases, they will use the Docker image for the service. In both cases the `run` recipes define the necessary environment variables, set at their defaults.

If you need to run a couple of the services together you can `make run` them in separate terminals. This can be handy if you want to do iterative development of one service while checking that it is talking the correct way with one or more of the other services.

### Integration testing with `docker-compose`

To test the integration between services use the `docker-compose.yaml` file. To bring up the whole stack,

```sh
make run
# or
docker-compose up
```

Or, to just bring up one or two of the services _and_ their dependents,

```sh
docker-compose up director worker
```

### Integration testing with `minikube` and `kompose`

To test deployment within a Kubernetes cluster upu can use [Minikube](https://minikube.sigs.k8s.io/docs/) and [Kompose](http://kompose.io/),

```sh
minikube start
make run-in-minikube
```

> The `run-in-minikube` recipe sets up Minikube to be able to do local builds of images, rather than pulling them down from Docker Hub, build the images, and then runs `kompose up`.

The `minikube dashboard` is really useful for debugging. And don't forget to `minikube stop` when you're done!

---

The `director` directory contains the Django application. In most instances you can set up the Python environment using
`make` commands:

```bash
make setup  # set up the virtual environment and install requirements
make -C director create-devdb  # populate the dev DB with test accounts (usernames == passwords)
make run  # start the Django server
```

Alternatively you can follow standard Python virtualenv setup methods to put the virtualenv in your preferred location,
then start server with `manage.py runserver` etc. 

### Contributing

If you would like to contribute to Stencila Hub, please see the [developer guidelines](CONTRIBUTING.md).

### Continuous integration

We use Travis as a continuous integration server. Currently, the Travis configuration will do linting, run tests and 
build the production Docker image. See [here](https://travis-ci.org/stencila/hub) for the latest build and 
[`travis.yml`](travis.yml) for the configuration.

### Linting

Three forms of code quality analysis are currently available. 

- `make -C director code` runs [`flake8`](http://flake8.pycqa.org) for code style checking.

- `make -C director types` runs [`mypy`](http://mypy-lang.org/) for static type checking using the 
  [`director/mypy.ini`](director/mypy.ini) config file.

- `make -C director docs` runs [`pydocstyle`](http://www.pydocstyle.org) for checks on docstrings.

Running `make lint` will perform all three checks.

We use Codeclimate for additional monitoring of code quality and maintainability, beyond that provided by running the 
linting commands described above. See [here](https://codeclimate.com/github/stencila/hub) for current status.

### Testing

Test coverage reports, generated on Travis, are available on Codecov [here](https://codecov.io/gh/stencila/hub).

### Dependency updates

We use PyUp to keep track of security and regular updates to packages this repo depends upon. See 
[here](https://pyup.io/repos/github/stencila/hub) for current status and [`pyup.yml`](pyup.yml) for the configuration. 
PyUp is currently configured to create an automatic pull request each week with any new updates that are necessary.
