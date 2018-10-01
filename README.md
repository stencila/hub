<div align="center">
	<img src="http://stenci.la/img/logo-name.png" alt="Stencila" style="max-width:200px">
</div>

[![Build](https://travis-ci.org/stencila/hub.svg?branch=master)](https://travis-ci.org/stencila/hub)
[![Coverage](https://codecov.io/gh/stencila/hub/branch/master/graph/badge.svg)](https://codecov.io/gh/stencila/hub)
[![Maintainability](https://api.codeclimate.com/v1/badges/0d6cbfb262152e2b9242/maintainability)](https://codeclimate.com/github/stencila/hub/maintainability)
[![Updates](https://pyup.io/repos/github/stencila/hub/shield.svg)](https://pyup.io/repos/github/stencila/hub/)
[![License](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://opensource.org/licenses/Apache-2.0)

Stencila is an open source platform for authoring, collaborating on, and sharing data driven documents. This is the repository for the Stencila Hub.
The Hub is the gateway to using Stencila on the web. The Hub allows users to access the full functionality of Stencila without having to configure anything on their local machines.

We want to avoid reinventing the wheel and instead provide a way of connecting existing services. There are already plenty of places to store files (e.g. Dropbox, Google Drive, Github) and places to edit files (e.g. Google Docs, Microsoft Office Online).

As far as possible we want to connect these providers with each other and with Stencila’s execution contexts for languages like R and Python as provided by the Stencila Cloud. We’ll do this by using providers’ APIs, Stencila’s document converters (e.g. to convert a Markdown doc on Github into a Google Doc), and Stencila’s plugins (e.g. to execute Python code from within that Google Doc).


## Implementation

Stencila Hub is implemented using [Django](https://www.djangoproject.com/), [Node.js](https://nodejs.org/en/), [Nginx](http://nginx.org/) and Docker
(with the latter two being crucial for the Hub to cooperate with Stencila Cloud).

The projects in Stencila Hub can be created  by adding files from multiple sources (:sparkles: under development :sparkles:) and in multiple formats. The conversion between
the formats is achieved by using [Stencila Converters](https://github.com/stencila/convert) which can be used as an inependent command line tool.

The interactive code cells in the documents and sheets in Stencila Hub projects can be executed thanks to [Stencila Cloud](https://github.com/stencila/cloud)
where hosts for execution contexts sit in Docker containers on a Kubernetes Cluster.

## Architecture

Stencila Hub consists of three roles: `director`, `editor` and `router`. Each of these roles can be set up for development separately. That is, you can contribute to the
Hub getting these roles set up and run independently.

> Note: Whilst the deployment of these roles is done in Docker Containers, you should develop in your local environment rather than in the Docker container,
(which can be set up for each of these roles) because this way you will be able to preview the changes you are making in the source code.

The specifications of the roles:

* Director - Django app containing most of the application logic.
* Editor - Node.js server and JS client (using stencila/stencila UI) for editing.
* Router - Nginx config that routes requests to Director and Editor.


### Director
The Director is split into three main Django “apps”: Projects, Editors, Hosts and Checkouts. Most of these are currently very lightweight
but separating them into these apps is intended to encourage a higher degree of modularity and independence.

#### Projects
A project is a collection of documents (including text, sheets, code, data documents/files). The Django `Project` model is a base class for various types of projects representing collections of files stored in various locations by alternative providers (e.g. Github, Dropbox). Currently the `FilesProject`, representing a collection of files stored by Stencila (currently, but not necessarily, stored in a Google Cloud Storage bucket), is the only `Project` class implemented. `GithubProject`, `DropboxProject` etc are planned.

Each `Project` class implements a `pull(): zip` method which fetches of the contents of the project and returns it as a zip archive and a `push(zip)` method which sends the updated contents of the project to the provider.

The semantics of `pull` and `push` may differ for different providers and different users. For example, a `GithubProject.push()` method may be equivalent to a Git `commit + push` if the user has write access to the repo, but equivalent to a `fork + pull request` if the user does not.

### Editor

Editors are used to edit documents. The Django `Editor` model is a base class for various types of editors (e.g. [Texture](http://substance.io/texture/), Google Sheets). Each editor instance is actually an editor "session" (connecting to Stencila Cloud to give users access to execution contexts)
and will map directly to a document (or collection of documents) for that editor class (e.g. a Google sheet).

Just like projects, each `Editor` class implements a `push(zip)` method which sends the contents of the project (which may just be a single document) to the provider (e.g. Google Docs) and a `pull(): zip` method which fetches the contents of the project from the editor and returns it as a zip archive. These methods will usually involve a format conversion step. For example, if the user wanted to edit a Markdown document in Google Docs, the `GoogleDocEditor` would implement `push()` and `pull()` methods like so:

* `push()` would convert the Markdown to Word, and send the `docx` file to Google via the [Google Drive API](https://developers.google.com/drive/api/v2/about-sdk)
* `pull()` would fetch the `docx` via the API and convert it back to Markdown.

Conversion is done via Stencila Converters (which in turn wrap Pandoc and other useful tools).

Currently only the `NativeEditor` class is implemented (with Texture being used as the editor). It converts incoming files to XML (compliant with the Dar format) and sends it to the editor role (mentioned above) which provides the same editor as in Stencila Desktop.

### Hosts

Hosts provide execution contexts (variable namespaces within R, Python etc) within execution environments (complete, reproducible computational environments). See the draft [API for a Host](https://stencila.github.io/specs/host.html).

The Django `Host` model is a base class for various types of hosts (although there may only need to be one class, the currently implemented `NativeHost` since the API should be uniform). Each `Host` model instance is actually a host "session" and may have different queue priorities and resource consumption limits. The hosts are for example deployed on [Stencila Cloud](http://cloud.stenci.la/). There may be multiple hosts available at multiple locations as the Cloud can be deployed within, for example,
a university cluster and the Stencila Hub will redirect the user to which ever host is closest and/or most suitable for the particular project (e.g. based on proximity to data).

Whereas the project and editor apps are mostly about hooking into alternative third party APIs, the `host` app requires the most development of modes and business logic (including metering of usage etc for billing).

### Checkouts

Checkouts are a combination of a `Project`, an `Editor` and a `Host`. They represent a project editing and execution session; a working copy of a project. When a user “opens” a project they are creating a checkout.

Currently, a user can select which project to open but not which Editor or Host (both default to the single, native implementation). In the future, the user might be able to select where to edit a project and which host to execute it on (and/or have some defaults to select the best combination for them).

Currently, checkouts use a primitive locking (well actually just a warning) to avoid multiple editor sessions for the same project. In the future, checkouts may be collaborative ie. involving more than one user.




## Development setup

If you would like to contribute to Stencila Hub, please see the [developer guidelines](CONTRIBUTING.md).


### Continuous integration

We use Travis as a continuous integration server. Currently, the Travis configuration will do linting, run tests and build the production Docker image. See [here](https://travis-ci.org/stencila/hub) for the latest build and [`travis.yml`](travis.yml) for the configuration.

### Test coverage reporting

Test coverage reports, generated on Travis, are available on Codecov [here](https://codecov.io/gh/stencila/hub).

### Code maintainability reporting

We use Codeclimate for additional monitoring code quality and maintainability, beyond that provided by Pyllama. See [here](https://codeclimate.com/github/stencila/hub) for current status.

### Dependency updates

We use PyUp to keep track of security and regular updates to packages this repo depends upon. See [here](https://pyup.io/repos/github/stencila/hub) for current status and [`pyup.yml`](pyup.yml) for the configuration. PyUp is currently configured to create an automatic pull request each week with any new updates that are necessary.
