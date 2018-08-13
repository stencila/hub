<div align="center">
	<img src="http://stenci.la/img/logo-name.png" alt="Stencila" style="max-width:250px">
</div>

Stencila is an open source platform for authoring, collaborating on, and sharing data driven documents. This is the repository for the Stencila Hub.

## Contribute

We are always keen to get comments and suggestions for ways to improve the Stencila Hub. Chat with us in the [stencila/stencila room](https://gitter.im/stencila/stencila) on Gitter or using the in-app intercom (if you have a user account).

If you have specific suggestions or have found a bug, please [create an issue](https://github.com/stencila/hub/issues/new). If you have any issue related to security, please send us an email at security@stenci.la, rather than create a Github issue.

Code contributions will be gratefully received! Please send use a pull request.

## Develop

Stencila Hub consists of three roles: `director`, `editor` and `router`. Each of these roles can be set up for development separately. That is, you can contribute to the
Hub getting these roles set up and run independently. You should develop in your local environment rather than in the Docker container, which can be set up for each of these
	roles) because this way you will be able to preview the changes you are making in the source code.

The Docker containers (`stencila/hub-director`, `stencila/hub-editor`, `stencila/hub-router`) are used for deployment.

### Run `director`

To run the `director` locally:

```bash
make director-run
```

This will setup virtual environment installing all required packages. **Note** You need to have `python3` and `pip3` installed on your machine.

When you are running the `director` for the first time, you will need to set up the database for Django. For the development we use `sqlite3`. In oder to get that done:

```bash
make director-create-devdb
```
You should now be set up for development and access the development server at `http://127.0.0.1:8000/`

To run the `director` in Docker:

```bash
make director-build director-rundocker
```

**Note** This will first build the Docker file (`hub-director`) and then run director in that Docker container. If you make changes to the source code after you build the,
Docker file they will not be reflected in the container. You will have to rebuild it. Hence, it is recommended that you develop the Hub in your local environment.

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
