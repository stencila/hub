<div align="center">
	<img src="http://stenci.la/img/logo-name.png" alt="Stencila" style="max-width:150px">
</div>
<br>

[![Build Status](https://dev.azure.com/stencila/stencila/_apis/build/status/stencila.hub?branchName=master)](https://dev.azure.com/stencila/stencila/_build/latest?definitionId=5&branchName=master)
[![Coverage](https://codecov.io/gh/stencila/hub/branch/master/graph/badge.svg)](https://codecov.io/gh/stencila/hub)
[![License](https://img.shields.io/badge/License-Apache%202.0-3262eb.svg)](https://opensource.org/licenses/Apache-2.0)

Stencila is an open source platform for authoring, collaborating on, and sharing executable documents. This is the 
repository for the [Stencila Hub](https://hub.stenci.la).


## ✨ Features

A brief overview of features implemented by the Stencila Hub. These are current features, more are planned as we are 
under active development (specific features are labelled with the Future Feature Unicorn 🦄).

We also welcome your suggestions or code contributions for feature you'd like to see.

### Authentication

- Store user credentials securely inside the Hub database, or
- Authenticate with third party services such as Github, Google, Twitter and Orcid

### Projects

- Create projects
    - Upload, manage and edit files and data in the browser
- Link remote sources (Github, Google Drive 🦄 and Dropbox 🦄)
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

## ⚙️ Services

Stencila Hub consists of several services, each with it's own sub-folder. The `README.md` file for each service (🦄 not all of these are written yet) provides further details on the service, including its purpose, the current and potential alternative technical approaches, and tips for development:

* [`router`](router): A [Nginx](https://nginx.org/) server that routes requests to other services.
* [`director`](director): A [Django](https://www.djangoproject.com/) project containing most of the application logic.
* [`broker`](broker): A [RabbitMQ](https://www.rabbitmq.com/) instance that acts as a message queue broker.
* [`worker`](worker): A [Celery](https://docs.celeryproject.org) process that runs jobs from the broker's queue.
* [`scheduler`](scheduler): A Celery process that places periodic, scheduled jobs on the broker's queue.
* [`overseer`](overseer): A Celery process that monitors events associated with workers and job queues.
* [`database`](database): A [PostgreSQL](https://www.postgresql.org/) database used by the director.
* [`monitor`](monitor): A [Prometheus](https://prometheus.io/) instance that monitors the health of the other services.

## 🛠️ Develop

### Prerequisites

The prerequisites for development vary somewhat by service (see the service `README.md`s for more details). However, most of the services will require you to have at least one of the following installed:

- [Docker Engine](https://docs.docker.com/engine/)
- [Python >=3.7](https://www.python.org/)
- [Node.js >=12](https://nodejs.org/)

To run the service integration tests described below you will need:

- [Docker Compose](https://docs.docker.com/compose/)

and/or,

- [Minikube](https://minikube.sigs.k8s.io/docs/)
- [Kompose](https://kompose.io/)

### Getting started

The top level `Makefile` contains recipes for common development tasks e.g `make lint`. To run all those recipes, culminating in standing up containers for each of the services, simply do:

```sh
make
```

The top level `make` recipes mostly just invoke the corresponding recipe in the `Makefile` for each service. You can run them individually by either `cd`ing into the service's folder or using the `make -C` option e.g. to just run the `director` service,

```sh
make -C director run
```

> 💁 Tip: The individual `run` recipes are useful for quickly iterating during development and, in the case of the `director`, will hot-reload when source files are edited. Where possible, the `run` recipes will use a local Python virtual environment. In other cases, they will use the Docker image for the service. In both cases the `run` recipes define the necessary environment variables, set at their defaults.

> 💁 Tip: If you need to run a couple of the services together you can `make run` them in separate terminals. This can be handy if you want to do iterative development of one service while checking that it is talking correctly to one or more of the other services.

> 🛈 Info: We use `Makefile`s throughout this repo because `make` is a ubiquitous and language agnostic development tool. However, they are mostly there to guide and document the development workflow. You may prefer to bypass `make` in favour of using your favorite tools directly e.g. `python`, `npx`, PyCharm, `pytest`, VSCode or whatever.

### Linting and formatting

Some of services define code linting and formatting recipes. Often they get run together e.g.

```sh
make format lint
```

### Unit testing

Some of services define unit tests. Run them using,

```sh
make test
```

Or, with coverage,

```sh
make cover
```

> 🛈 Info: Test coverage reports are generated on CI for each push and are available on Codecov [here](https://codecov.io/gh/stencila/hub).


### Integration testing

#### With `docker-compose`

To test the integration between services, use the `docker-compose.yaml` file. To bring up the whole stack of services,

```sh
docker-compose up --build
```

Or, to just bring up one or two of the services _and_ their dependents,

```sh
docker-compose up director worker
```

To create a development database for integration testing, stand up the `database` service and then use the `director`'s `create-devdb-pg` recipe to populate it:

```sh
docker-compose start database
make -C director create-devdb-pg
```

> 💁 Tip: [pgAdmin](https://www.pgadmin.org/) is useful for inspecting the development PostgreSQL database

#### With `minikube` and `kompose`

To test deployment within a Kubernetes cluster you can use [Minikube](https://minikube.sigs.k8s.io/docs/) and [Kompose](http://kompose.io/),

```sh
minikube start
make run-in-minikube
```

> 🛈 Info: the `run-in-minikube` recipe sets up Minikube to be able to do local builds of images (rather than pulling them down from Docker Hub), then builds the images in Minikube and runs `kompose up`.

> 💁 Tip: The `minikube dashboard` is really useful for debugging. And don't forget to `minikube stop` when you're done!

### Committing

Commit messages should follow the [conventional commits](https://www.conventionalcommits.org/) specification. This is important (but not required) because commit messages are used to determine the semantic version of releases (and thus deployments) and to generate the project's [CHANGELOG.md](CHANGELOG.md). If appropriate, use the sentence case service name as the scope (to help make both `git log` and the change log more readable). Some examples,

- `fix(Monitor): Fix endpoint for scraping metrics`
- `feat(Director): Add pulling from Google Drive`
- `docs(README): Add notes on commit messages`

### Dependency updates

We use Renovate to keep track of updates to packages this repo depends upon. For more details, see 
the list of currently open and scheduled [Renovate PRs](https://github.com/stencila/hub/issues/302) and the `renovate` configuration in [`package.json`](package.json).

## 🚀 Continuous integration and deployment

We use Azure Pipelines as a continuous integration (CI) service. On each push, the CI does linting and run tests. On each tag, the Docker image for each service is built and pushed to Docker Hub:

- [Stencila Hub's Azure Pipeline](https://dev.azure.com/stencila/stencila/_build?definitionId=5&_a=summary)
- [Stencila Hub's images on Docker Hub](https://hub.docker.com/u/stencila)

Continuous deployment (CD) to https://hub.stenci.la is done using [FluxCD](https://fluxcd.io/) from another repository:

- [Stencila's continuous deployment and status reporting repo](https://github.com/stencila/gaia)
- [Stencila's status page](https://status.stenci.la/)

