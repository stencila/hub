# Stencila Hub Worker

## Purpose

The `worker` service processes jobs sent to one or more job queues. It is designed to be able to run either within, or outside, of the cluster that the other services are running. For example, users may wish to run their own `worker` instances, listening to their account's virtual host on the `broker`.

## Approach

The `worker` is a Celery process. Jobs are defined as Python classes in the [`jobs`](jobs) directory. However, jobs are not restricted to being implemented in Python; they may make use of other processes (see `SubprocessJob`), Docker containers, or Kubernetes pobs.

## Testing

Each of the jobs should have at least one `*_test.py` file. You can run all the tests like this,

```sh
make test
```

Or, with coverage, using,

```sh
make cover
```

If you want to run tests individually, use `pytest` directly e.g. to only run the tests for the convert job:

```sh
./venv/bin/pytest jobs/convert
```

Some of the jobs, in particular those in [`jobs/pull`](jobs/pull), involve making HTTP requests. To speed up test runs and to allow them to be run offline, we use `pytest-recording` to record requests and their responses. To enable this for a test add the `@pytest.mark.vcr` decorator and run the test once with `--record-mode=rewrite` e.g.

```bash
./venv/bin/pytest --record-mode=rewrite jobs/pull/elife_test.py
```

The generated YAML files in the `casettes` folder should be committed. If needs be, you can run tests again with `rewrite` mode to update the casettes.
