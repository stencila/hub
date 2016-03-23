# Worker

The `worker` role hosts host language (e.g. R) sessions within Docker container instances. The Python script [`worker.py`](worker.py) acts as an agent to the `director` for starting, stopping and providing information on sessions. 

Docker needs to be installed and then use `make worker-rundev` to run locally during development or use the provided Upstart configuration file.
