# Stencila Hub Monitor

## Purpose

The `monitor` is the Hub's application monitoring service. It collects and stores metrics on the health of the other services in the Hub (and on its self). Time series of these metrics can be queried and displayed.

## Solution

We use [Prometheus](https://prometheus.io/), a popular open-source application monitoring project orignally developed at SoundCloud.

Other services use so called "exporters" to expose metrics that Prometheus periodically scrapes, usually from the `/metrics` endpoint. For example, the `director` uses the `django_prometheus` Python package as an exporter and the `broker` uses the `rabbitmq_prometheus` plugin.

Prometheus exposes a simple tool for visualization of metrics at http://localhost:9090/graph. For example, a [graph of the `up` metric for each of the services monitored](http://localhost:9090/graph?g0.range_input=1h&g0.expr=up&g0.tab=0). The `router` provides a reverse proxy to this tool at `/internal/monitor/graph`.

Prometheus also exposes a HTTP API which can be queried to obtain time series of current values of metrics e.g. http://localhost:9090/internal/monitor/api/v1/query?query=up

http://localhost:9090/api/v1/query_range?query=up&start=1588618000&end=1588619900&step=15


## Alternatives

Prometheus has a detailed [comparison with alternatives](https://prometheus.io/docs/introduction/comparison/).
