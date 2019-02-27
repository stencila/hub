## Stencila Desktop on Stencila Hub

Stencila Desktop is our prototype of an office suite for reproducible research. It builds on top of Texture by adding reproducible elements like code cells, reproducible figures, and spreadsheets. This sub-folder provides a deployment of Stencila Desktop as a microservice within Stencila Hub.

### Run locally

To run locally, in the top-level folder run,

```bash
make desktop-run
```

You can then access the test Dar at http://localhost:4000/desktop


### Run within Docker

```bash
make desktop-rundocker
```

This will mount the `dars` folder into the Docker container so you should be able to access the test Dar via the same URL http://localhost:4000/desktop. Note that this is a test development setup only and due to how the `dars` folder is mounted, and because the container runs as non-root user, that you won't be able to save any changes.


### Run via `router`

The [`router`](../router) routes requests to Stencila Hub's various microservices. To test that is working run,

```bash
make router-rundocker
# Then, in a separate terminal
make desktop-rundocker
```

Now you should be able to use Stencila Desktop at http://localhost:3000/desktop (note the different port number).
