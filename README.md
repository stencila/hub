<div align="center">
	<img src="https://stenci.la/img/stencila/stencilaLogo.svg" alt="Stencila" style="max-width:150px">
</div>
<br>

|Build|[![Build Status](https://dev.azure.com/stencila/stencila/_apis/build/status/stencila.hub?branchName=master)](https://dev.azure.com/stencila/stencila/_build?definitionId=5) [![Coverage](https://codecov.io/gh/stencila/hub/branch/master/graph/badge.svg)](https://codecov.io/gh/stencila/hub)|
|:-|:-|
|**Services**|[![Router](https://img.shields.io/docker/v/stencila/hub-router?label=router&logo=docker)](https://hub.docker.com/r/stencila/hub-router) [![Manager](https://img.shields.io/docker/v/stencila/hub-manager?label=manager&logo=docker)](https://hub.docker.com/r/stencila/hub-manager) [![Assistant](https://img.shields.io/docker/v/stencila/hub-assistant?label=assistant&logo=docker)](https://hub.docker.com/r/stencila/hub-assistant) [![Broker](https://img.shields.io/docker/v/stencila/hub-broker?label=broker&logo=docker)](https://hub.docker.com/r/stencila/hub-broker) [![Worker](https://img.shields.io/docker/v/stencila/hub-worker?label=worker&logo=docker)](https://hub.docker.com/r/stencila/hub-worker) [![Overseer](https://img.shields.io/docker/v/stencila/hub-overseer?label=overseer&logo=docker)](https://hub.docker.com/r/stencila/hub-overseer) [![Database](https://img.shields.io/docker/v/stencila/hub-database?label=database&logo=docker)](https://hub.docker.com/r/stencila/hub-database) [![Cache](https://img.shields.io/docker/v/stencila/hub-cache?label=cache&logo=docker)](https://hub.docker.com/r/stencila/hub-cache)[![monitor](https://img.shields.io/docker/v/stencila/hub-monitor?label=monitor&logo=docker)](https://hub.docker.com/r/stencila/hub-monitor)|
|**Clients**| [![PyPI](https://img.shields.io/pypi/v/stencila.hub?logo=pypi)](https://pypi.org/project/stencila.hub/) [![NPM](https://img.shields.io/npm/v/@stencila/hub-client?logo=npm)](https://www.npmjs.com/package/@stencila/hub-client)|


<br>

## 👋 Introduction

Stencila is an platform of open source tools for authoring, collaborating on, and sharing executable documents. This is the repository for the [Stencila Hub](https://hub.stenci.la) which deploys these tools as a service and integrates them with other tools and services (e.g. Google Docs, GitHub).

## ⚙️ Services

Stencila Hub consists of several services, each with it's own sub-folder. The `README.md` file for each service provides further details on the service, including its purpose, the current and potential alternative technical approaches, and tips for development.

* [`router`](router): A [Nginx](https://nginx.org/) server that routes requests to other services.
* [`manager`](manager): A [Django](https://www.djangoproject.com/) project containing most of the application logic.
* [`assistant`](manager/manager/assistant.py): A [Celery](https://docs.celeryproject.org) worker that runs asynchronous _tasks_ on behalf of the `manager`.
* [`worker`](worker): A Celery process that runs _jobs_ on behalf of users.
* [`broker`](broker): A [RabbitMQ](https://www.rabbitmq.com/) instance that acts as a message queue broker for tasks and jobs.
* [`scheduler`](scheduler): A Celery process that places periodic, scheduled tasks and jobs on the broker's queue.
* [`overseer`](overseer): A Celery process that monitors events associated with workers and job queues.
* [`database`](database): A [PostgreSQL](https://www.postgresql.org/) database used by the manager.
* [`cache`](cache): A [Redis](https://redis.io/) store used as a cache by the `manager` and as a result backend for Celery
* [`steward`](steward): Manages access to cloud storage for the `worker` and other services.
* [`monitor`](monitor): A [Prometheus](https://prometheus.io/) instance that monitors the health of the other services.

## 🤝 Clients

The Hub exposes a public API, https://hub.stenci.la/api. API client packages, generated from the [Hub's OpenAPI Schema](https://hub.stenci.la/api/schema), are available in this repository for the following languages:

- [`python`](clients/python)
- [`typescript`](clients/typescript)

Client packages for other languages will be added based on demand. Please don't hesitate to ask for a client for your favorite language!

## 📜 Documentation

* User focussed documentation is available in the [Hub collection](http://help.stenci.la/en/collections/2413959-stencila-hub) of our help site.

* As mentioned above, most of the individual services have a `README.md` files.

* The code generally has lots of documentation string and comments, so "Use the source, Luke".

* To get an overview of the functionality provided check out the automatically generated [page screenshots](https://stencila.github.io/hub/manager/snaps/) (see [`manager/README.md`](manager/README.md) for more details on how and why these are generated).

## 🛠️ Develop

### Prerequisites

The prerequisites for development vary somewhat by service (see the service `README.md`s for more details). However, most of the services will require you to have at least one of the following installed (with some examples of how to install for Ubuntu and other Debian-based Linux plaforms):

- [Python >=3.7](https://www.python.org/) with `pip` and `venv` packages:
  - `sudo apt-get install python3 python3-pip python3-venv`
- [Node.js >=12](https://nodejs.org/) and NPM
  - `sudo apt-get install nodejs npm`
- [Docker Engine](https://docs.docker.com/engine/)

To run the service integration tests described below you will need:

- [Docker Compose](https://docs.docker.com/compose/)

and/or,

- [Minikube](https://minikube.sigs.k8s.io/docs/)
- [Kompose](https://kompose.io/)

### Getting started

The top level `Makefile` contains recipes for common development tasks e.g `make lint`. To run all those recipes, culminating in building containers for each of the services (if you have `docker-compose` installed), simply do:

```sh
make
```

> 💬 Info: We use `Makefile`s throughout this repo because `make` is a ubiquitous and language agnostic development tool. However, they are mostly there to guide and document the development workflow. You may prefer to bypass `make` in favour of using your favorite tools directly e.g. `python`, `npx`, PyCharm, `pytest`, VSCode or whatever.

The top level `make` recipes mostly just invoke the corresponding recipe in the `Makefile` for each service. You can run them individually by either `cd`ing into the service's folder or using the `make -C` option e.g. to just run the `manager` service,

```sh
make -C manager run
```

> 💁 Tip: The individual `run` recipes are useful for quickly iterating during development and, in the case of the `manager`, will hot-reload when source files are edited. Where possible, the `run` recipes will use a local Python virtual environment. In other cases, they will use the Docker image for the service. In both cases the `run` recipes define the necessary environment variables, set at their defaults.

> 💁 Tip: If you need to run a couple of the services together you can `make run` them in separate terminals. This can be handy if you want to do iterative development of one service while checking that it is talking correctly to one or more of the other services.

### Linting and formatting

Most of the services define code linting and formatting recipes. It is often useful to run them sequentially in one command i.e.

```sh
make format lint
```

### Unit testing

Some services define unit tests. Run them all using,

```sh
make test
```

Or, with coverage,

```sh
make cover
```

> 💬 Info: Test coverage reports are generated on CI for each push and are available on Codecov [here](https://codecov.io/gh/stencila/hub).


### Integration testing

#### Manually running each service

The most hands-on way of testing the integration between services is to run each of them locally. 

First, create a seed SQLite development database,

```sh
make -C manager create-devdb-sqlite
```

Note that this will destroy any existing `manager/dev.sqlite3` database. If you want to update your development database to a newer version of the database schema do this instead,

```sh
make -C manager migrate-devdb
```

Then in *separate* terminal consoles run the following `make` commands,

```sh
make -C manager run
```

```sh
make -C broker run
```

```sh
make -C cache run
```

```sh
make -C overseer run
```

```sh
make -C worker run
```

At the time of writing, those services provide for most of use cases, but you can of course also run other services locally e.g. `router` if you want to test them.

#### With `docker-compose`

The `docker-compose.yaml` file provides an easier way of integration testing. First, ensure that all of the Docker images are built:

##### Building images

```sh
make -C manager static # Builds static assets to include in the `manager` image
docker-compose up --build # Builds all the images
```

##### Creating a seed development database

Create a seed development database within the `database` container by starting the service:

```sh
docker-compose start database
```

and, then in another console, sending the commands to the Postgres server to create the database,

```sh
make -C manager create-devdb-postgres
```

If you encounter errors related to the database already existing, it may be because the you previously ran these commands. In those cases we recommend removing the existing container using,

```sh
docker-compose stop database
docker rm hub_database_1
```

and running the previous commands again.

> 💁 Tip: [pgAdmin](https://www.pgadmin.org/) is useful for inspecting the development PostgreSQL database

##### Running services

Once you have done the above, to bring up the whole stack of services,

```sh
docker-compose up
```

The `router` service, which acts as the entry point, should be available at http://localhost:9000.

Or, to just bring up one or two of the services _and_ their dependents,

```sh
docker-compose up manager worker
```

#### With `minikube` and `kompose`

To test deployment within a Kubernetes cluster you can use [Minikube](https://minikube.sigs.k8s.io/docs/) and [Kompose](http://kompose.io/),

```sh
minikube start
make run-in-minikube
```

> 💬 Info: the `run-in-minikube` recipe sets up Minikube to be able to do local builds of images (rather than pulling them down from Docker Hub), then builds the images in Minikube and runs `kompose up`.

> 💁 Tip: The `minikube dashboard` is really useful for debugging. And don't forget to `minikube stop` when you're done!

> 💁 Tip: Instead of using `minikube` you might want to consider lighter weight alternatives such as `kind`, `microk8s`, or `k3s` to run a local Kubernetes cluster.

### Committing

Commit messages should follow the [conventional commits](https://www.conventionalcommits.org/) specification. This is important (but not required) because commit messages are used to determine the semantic version of releases (and thus deployments) and to generate the project's [CHANGELOG.md](CHANGELOG.md). If appropriate, use the sentence case service name as the scope (to help make both `git log` and the change log more readable). Some examples,

- `fix(Monitor): Fix endpoint for scraping metrics`
- `feat(Director): Add pulling from Google Drive`
- `docs(README): Add notes on commit messages`

### Dependency updates

We use Renovate to keep track of updates to packages this repo depends upon. For more details see  the list of currently open and scheduled [Renovate PRs](https://github.com/stencila/hub/issues/302) and the `renovate` configuration in [`package.json`](package.json).

## 🚀 Continuous integration

We use Azure Pipelines as a continuous integration (CI) service. On each push, the CI does linting and runs tests and semantic releases made (if there are commits since the last tag of types `feat` or `fix`). On each tag, if there are commits in a service's directory since the last tag, the Docker image for the service is built and pushed to Docker Hub (that is why Docker images do not necessarily have the same tag):

- [Stencila Hub's Azure Pipeline](https://dev.azure.com/stencila/stencila/_build?definitionId=5&_a=summary)
- [Stencila Hub's images on Docker Hub](https://hub.docker.com/u/stencila)
