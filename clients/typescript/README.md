# Stencila Hub Typescript Client

[![npm version](https://badge.fury.io/js/%40stencila%2Fhub-client.svg)](https://www.npmjs.com/package/@stencila/hub-client)

This Typescript package provides a client for the Stencila Hub API. It is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) from our [OpenAPI Schema](https://hub.stenci.la/api/schema).

The following should be supported:

- Environments
  * Node.js
  * Webpack
  * Browserify

- Language level
  * ES6

- Module system
  * CommonJS
  * ES6 module system

## Use

Install the package,

```sh
npm install @stencila/hub-client
```

Then, create a configuration containing your API token and pass it to the constructor of each of the [API classes](src/api) e.g.

```ts
import { Configuration, ProjectsApi } from '@stencila/hub-client'

// Create a configuration with the user's API token.
const config = new Configuration({
  apiKey: `Token ${STENCILA_HUB_TOKEN}`
})

// Pass the configuration to the API class constructor.
const api = new ProjectsApi(config)

// List all projects that are not public and that the user is
// a manager of.
const projects = await api.projectsList({
  public: false,
  role: 'manager'
})
```

See [tests](__tests__) for more examples.

## Develop

Both the generation and testing of the client require a local instance of the `manager` service to be running. To start that, at the top level of this repo, run

```sh
make -C manager run
```

### Generating client

To regenerate the client, at the top level of this repo, run

```sh
make -C clients typescript
```

There are two primary options for customizing the files this package:

1. Override the [Mustache templates](https://github.com/OpenAPITools/openapi-generator/tree/master/modules/openapi-generator/src/main/resources/typescript-fetch) and place them in the [`templates`](templates) folder

2. Turn off generation by adding the file to [`.openapi-generator-ignore`](.openapi-generator-ignore) (as we do for this `README.md` in fact!).


### Running tests

Tests run against a local instance of the `manager` service. So start that, generate the `src` directory, and then run the tests from in this directory,

```sh
npm test
```

## Continuous deployment

This client package is regenerated on each release and published on NPM. Tests of this package are currently not run on each release.
