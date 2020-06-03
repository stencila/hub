## Develop

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
