# Curator

The `curator` role manages the component repositories for Stencila components. It consists of:

 - a Python script [`curator.py`](curator.py) which exposes repos via a REST API for `director` to use to do stuff like fork repos

 - a Go script [`curator.go`](curator.go) which implements the [Git Smart HTTP Transport](https://git-scm.com/blog/2010/03/04/smart-http.html) for Git clients to access component repos (proxied and authorized by `director`)

During development, run `make curator-py-rundev` and `make director-go-rundev` in two separate consoles so you can see the output from each. You can then test the Python script using curl e.g.

```
curl -X POST http://localhost:7310/resetup
```

, or when arguments need to be supplied,

```
curl -X POST -H "Content-Type: application/json" -d '{"address":"stencila/blog/introducing-sheets","type":"stencil"}' http://localhost:7310/init
```

There are Upstart configurations for both scripts also.
