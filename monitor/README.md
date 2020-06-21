# Stencila Hub Monitor

## Purpose

The `monitor` is the Hub's application monitoring service. It collects and stores metrics on the health of the other services in the Hub (and on its self). Time series of these metrics can be queried and displayed.

## Solution

We use [Prometheus](https://prometheus.io/), a popular open-source application monitoring project orignally developed at SoundCloud.

Other services use so called "exporters" to expose metrics that Prometheus periodically scrapes, usually from the `/metrics` endpoint. For example, the `manager` uses the `django_prometheus` Python package as an exporter and the `broker` uses the `rabbitmq_prometheus` plugin.

Prometheus exposes a simple tool for visualization of metrics at http://localhost:9090/graph. For example, a graph of the `up` metric for each of the services monitored:


http://localhost:9090/internal/monitor/graph?g0.range_input=1h&g0.expr=up&g0.tab=0


Prometheus also exposes a HTTP API which can be queried to obtain time series of current values of metrics e.g. 


http://localhost:9090/internal/monitor/api/v1/query?query=up


The `router` provides a reverse proxy to the `monitor`'s graph interface and API at `/internal/monitor`.

## Alternatives

Prometheus has a detailed [comparison with alternatives](https://prometheus.io/docs/introduction/comparison/).
