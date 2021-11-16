FROM prom/prometheus:v2.31.1

ADD prometheus.yml /etc/prometheus/

CMD [ \
  "--config.file=/etc/prometheus/prometheus.yml", \
  "--storage.tsdb.path=/prometheus", \
  "--storage.tsdb.retention.size=8GB", \
  "--storage.tsdb.retention.time=15d", \
  "--web.external-url=http://localhost:9090/internal/monitor" \
]
