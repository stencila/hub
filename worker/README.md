# Stencila Hub Worker

## Testing

Some of the jobs, in particular those in [`jobs/pull`](jobs/pull), involve making HTTP requests. To speed up test and to allow them to be run offline, we use `pytest-recording` to record requests and their responses. To enable this for a test add the `@pytest.mark.vcr` decorator and run the test with `--record-mode=rewrite` e.g.

```bash
./venv/bin/pytest --record-mode=rewrite jobs/pull/elife_pull.py
```

The generated YAML files in the `casettes` folder should be commited. If needs be, you can run with `rewrite` mode later to update the casettes.
