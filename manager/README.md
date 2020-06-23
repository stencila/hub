## Develop

### Local Development

Run the Django server using

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

### Page screenshots

There is a script that takes screenshots of all (well, almost all) of the pages at various viewport sizes. This can be useful for quickly scanning for broken pages and visual consistency. 

To generate the screenshots, make sure you have the dev server running locally,

```sh
make run
```

Then in another terminal,

```sh
make snaps
open snaps/index.html
```
