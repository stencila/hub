<div align="center">
	<img src="http://stenci.la/img/logo-name.png" alt="Stencila" style="max-width:150px">
</div>
<br>

[![Build](https://travis-ci.org/stencila/hub.svg?branch=master)](https://travis-ci.org/stencila/hub)
[![Coverage](https://codecov.io/gh/stencila/hub/branch/master/graph/badge.svg)](https://codecov.io/gh/stencila/hub)
[![Maintainability](https://api.codeclimate.com/v1/badges/0d6cbfb262152e2b9242/maintainability)](https://codeclimate.com/github/stencila/hub/maintainability)
[![Updates](https://pyup.io/repos/github/stencila/hub/shield.svg)](https://pyup.io/repos/github/stencila/hub/)
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

## Architecture

Stencila Hub consists of three roles: `director`, `editor` and `router`. Each of these roles can be set up for 
development separately. That is, you can contribute to the Hub getting these roles set up and run independently.

> Note: Whilst the deployment of these roles is done in Docker Containers, you should develop in your local environment 
rather than in the Docker container, (which can be set up for each of these roles) because this way you will be able to 
preview the changes you are making in the source code.

The specifications of the roles:

* Director - Django app containing most of the application logic.
* Editor - Node.js server and JS client (using stencila/stencila UI) for editing.
* Router - Nginx config that routes requests to Director and Editor.


## Development setup

The `director` directory contains the Django application. In most instances you can set up the Python environment using
`make` commands:

```bash
make director-venv  # set up the virtual environment and install requirements
make director-create-devdb  # populate the dev DB with test accounts (usernames == passwords)
make director-run  # start the Django server
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

- `make director-code` runs [`flake8`](http://flake8.pycqa.org) for code style checking.

- `make director-types` runs [`mypy`](http://mypy-lang.org/) for static type checking using the 
  [`director/mypy.ini`](director/mypy.ini) config file.

- `make director-docs` runs [`pydocstyle`](http://www.pydocstyle.org) for checks on docstrings.

Running `make director-lint` will perform all three checks.

We use Codeclimate for additional monitoring of code quality and maintainability, beyond that provided by running the 
linting commands described above. See [here](https://codeclimate.com/github/stencila/hub) for current status.

### Testing

Test coverage reports, generated on Travis, are available on Codecov [here](https://codecov.io/gh/stencila/hub).

### Dependency updates

We use PyUp to keep track of security and regular updates to packages this repo depends upon. See 
[here](https://pyup.io/repos/github/stencila/hub) for current status and [`pyup.yml`](pyup.yml) for the configuration. 
PyUp is currently configured to create an automatic pull request each week with any new updates that are necessary.


### Tagging a Release

Hub is versioned in three parts, in the format `major.minor.patch`, e.g. `1.2.3`, major = 1, minor =2 , patch = 3.

Incrementing the version number can be done with one of three `make` commands: `increment-patch`, `increment-minor` or 
`increment-major`. These will increment the patch, minor or major component, respectively. Then a new git commit will
be created. To create a tag of the commit, use the `make tag` command.

These steps can be combined into one with the `tag-patch`, `tag-minor` and `tag-major` commands, which will both 
increment the version and create the tag. It wil also push the tag and master to `origin`.
