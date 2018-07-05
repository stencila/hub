<div align="center">
	<img src="http://stenci.la/img/logo-name.png" alt="Stencila" style="max-width:250px">
</div>

Stencila is an open source platform for authoring, collaborating on, and sharing data driven documents. This is the repository for the Stencila Hub.

## Contribute

We are always keen to get comments and suggestions for ways to improve the Stencila Hub. Chat with us in the [stencila/stencila room](https://gitter.im/stencila/stencila) on Gitter or using the in-app intercom (if you have a user account). 

If you have specific suggestions or have found a bug, please [create an issue](https://github.com/stencila/hub/issues/new). If you have any issue related to security, please send us an email at security@stenci.la, rather than create a Github issue.

Code contributions will be gratefully received! Please send use a pull request.

## Develop


### Setup directories

Two directories are shared amongst roles: `storage` (for sharing project content across roles) and `secrets` (for sharing any secrets across roles). In production, these directories will usually be mounted as volumes (e.g. Kubernetes volumes). To keep [development and production environments as consistent as possible](https://12factor.net/dev-prod-parity), during development we simulate mounting these directories into each role by creating symlinks to a top level directory. See `make director-setup` and `make editor-setup` for doing this. If you prefer not to take this approach, you can override where `director` looks for these set the environment variables `STORAGE_DIR` and `SECRETS_DIR`.

### Run `director`

To run the `director` locally:

```bash
make director-run
```

Or, to run the `director` in Docker:

```bash
make director-build director-rundocker
```

### Run `editor`

To run the `editor` locally:

```bash
make editor-run
```

Or, to run the `editor` in Docker:

```bash
make editor-build editor-rundocker
```

### Run `router`

The `router` is configured to listen on port 3000 (to avoid clashing with other web servers which may already be listening to port 80)

```bash
make router-build router-rundocker
```

Now, you should be able to access the the Hub at http://localhost:3000. 
