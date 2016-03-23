<img src="http://static.stenci.la/img/logo-name-tagline-500.png" alt="Stencila" style="max-width:300px">

Stencila is an open source platform for authoring, collaborating on, and sharing data driven documents. This is the repository for the Stencila Hub at [https://stenci.la](https://stenci.la).

## Contributing

We are always keen to get comments and suggestions for ways to improve the Stencila Hub. Chat with us in the [stencila/stencila room](https://gitter.im/stencila/stencila) on Gitter or using the in-app intercom (if you have a user account). 

If you have specific suggestions or have found a bug, please [create an issue](https://github.com/stencila/hub/issues/new). If you have any issue related to security, please send us an email at security@stenci.la, rather than create a Github issue.

Code contributions will be gratefully received! Please send use a pull request.

## Fit

It is worth knowing how this repository fits in with other Stencila repos. There are three main strands to the Stencila platform:

- software *packages* for C++, R, Python and Javascript (and other languages to come) which allow users to author, render and publish stencils on their own machine are in the [stencila/stencila](https://github.com/stencila/stencila) repo

- a component *library* in which each component (i.e. a stencil or a sheet) has its own repo hosted at https://stenci.la/[component/address], for example `git clone https://stenci.la/demo/sheets/iris.git`

- the *hub* at https://stenci.la, contained in this repo, is the registry for components, server for component repositories and raw files (e.g. `sheet.tsv` for sheets), and host for component sessions

The hub uses the software *packages* (a) within Docker containers to allow online use of the components (the `worker` role) and (b) to extract meta data on components from their repos (the `curator` role), and (c) for the browser interface to components (served by the `director` role).

## Organization

This repo is organised into "roles". Most of these roles reflect a web service, or collection or web services:

- [`director`](director) : registry for components, accounts, users, sessions etc, authentication and authorization point, router and API server - a Django application

- [`curator`](curator) : curates and serves component repositories - a Python script which exposes repos via a REST API for `director` to use, a Go script which implements the [Git Smart HTTP Transport](https://git-scm.com/blog/2010/03/04/smart-http.html) for Git clients to access component repos (proxied and authorized by `director`)

- [`worker`](worker) : a machine that hosts component sessions in Docker container instances - Python script for taking an image of it (for replication), and a Python script `worker.py` which communicates with `director` for starting, stopping and providing information on sessions.

More details are provided for each of these roles in the `README.md` files of their respective directories. 

Each role has a port number (or multiple port numbers) and a private IP range assigned to it. These may be hard wired in code and config files and are used locally during development and in production. So it is worth specifying up front what they are:

Role      | IP range     | Service      | Port |
----------|--------------|--------------|------|
Director  | 10.0.1.25-49 | WSGI Django  | 7300 |
Curator   | 10.0.1.50-74 | `curator.py` | 7310 |
          |              | `curator.go` | 7311 | 
Worker    | 10.0.1.100-  | `worker.py`  | 7320 |
