<div align="center">
	<img src="http://stenci.la/img/logo-name.png" alt="Stencila" style="max-width:250px">
</div>

Stencila is an open source platform for authoring, collaborating on, and sharing data driven documents. This is the repository for the Stencila Hub.


## Architecture

Stencila Hub consists of three roles: `director`, `editor` and `router`. Each of these roles can be set up for development separately. That is, you can contribute to the
Hub getting these roles set up and run independently. You should develop in your local environment rather than in the Docker container, which can be set up for each of these
	roles) because this way you will be able to preview the changes you are making in the source code.

The Docker containers (`stencila/hub-director`, `stencila/hub-editor`, `stencila/hub-router`) are used for deployment.


## Development

If you would like to contribute to Stencila Hub, please see the [developer guidelines](CONTRIBUTING.md).
