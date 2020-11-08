# Stencila Hub Python Client

[![PyPI version](https://badge.fury.io/py/stencila.hub.svg)](https://pypi.org/project/stencila.hub)

This Python package provides a client for the Stencila Hub API. It is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) from our [OpenAPI Schema](https://hub.stenci.la/api/schema).

## Requirements

Python 3.4+

This package may work with Python 2.7 but only recent versions of Python are supported.

## Installation

Install from [PyPI](https://pypi.org/project/stencila.hub/) using:

```sh
pip3 install stencila.hub
```

_You may need to run `pip3` with root permission: `sudo pip3 install ...`_

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    try:
        api_response = api_instance.projects_list(
            account = 56, # The integer of the id of the account that the project belongs to
            role = 'author+', # The role that the currently authenticated user has on the project
            public = True, # Whether or not the project is public.
            search = 'foo', # A string to search for in the project `name`, `title` or `description`. (optional)
        )
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_list: %s\n" % e)
```

## Develop

### Generating client

The generation of the client requires a local instance of the `manager` service to be running. To start that, at the top level of this repo, run

```sh
make -C manager run
```

To regenerate the client, at the top level of this repo, run

```sh
make -C clients python
```

This will also generate Markdown documentation in the `docs` folder.

There are two primary options for customizing the files this package:

1. Override the [Mustache templates](https://github.com/OpenAPITools/openapi-generator/tree/master/modules/openapi-generator/src/main/resources/python) and place them in the [`templates`](templates) folder

2. Turn off generation by adding the file to [`.openapi-generator-ignore`](.openapi-generator-ignore).


### Running tests

First generate the client code files as described above, and then run:

```sh
tox
```

## Continuous deployment

This client package is regenerated on each release and uploaded to PyPI. Tests of this package are currently not run on each release.