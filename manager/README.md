## Develop

### Getting started

Run the Django server using,

``` sh
make run
```

Then, to automatically compile static assets on save and hot-reload in the browser, in another terminal run

``` sh
make run-watch
```

Some user interactions (e.g pulling and converting project sources) require `Job`s. For these jobs to be fulfilled you will need to run some of the other services,

1. `make -C ../broker run` to establish a job queue
2. `make -C ../overseer run` to update the manager with data on workers and jobs
3. `make -C ../worker run` to actually perform the jobs

### Linting

Four forms of code quality analysis are currently done: 

- `make lint-format` runs [`black`](https://pypi.org/project/black/) for code formatting checking.

- `make lint-code` runs [`flake8`](http://flake8.pycqa.org) for code style checking.

- `make lint-types` runs [`mypy`](http://mypy-lang.org/) for static type checking.

- `make lint-docs` runs [`pydocstyle`](http://www.pydocstyle.org) for checks on docstrings.

Running `make lint` will perform all three checks.

### End-to-end test and page screenshots

The script [`create_page_snaps.py`](scripts/create_page_snaps.py) will, for all of the `manager`'s pages  (well, almost all; it includes pages that are behind feature flags but excludes admin and some other pages),

- Records the response status code, response time and number be database queries (useful as an end-to-end and performance test)

- Takes screenshots of the entire screen at laptop and mobile viewport sizes (useful for quickly scanning for broken pages and visual consistency)

- Takes screenshots of specified page elements for use in user guides e.g. http://help.stenci.la/en/articles/4170083-create-an-organization (useful so that these stay up-to-date without having to be manually recreated)

To run this script, make sure you have the dev server running locally,

```sh
make run
```

Then in another terminal, run the script and open up the generated report.

```sh
make snaps
open snaps/index.html
```

This script is run as part of continuous integrations and the report published on GitHub Pages at https://stencila.github.io/hub/manager/snaps/.
