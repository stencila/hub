## Develop

### Local Development

Run the Django server by running

``` sh
make run
```

Then to automatically compile static assets on save and hot-reload in the browser, in another terminal run

``` sh
make run-watch
```

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
