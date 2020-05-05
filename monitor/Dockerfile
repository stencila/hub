FROM prom/prometheus

ADD prometheus.yml /etc/prometheus/

CMD [ \
  "--config.file=/etc/prometheus/prometheus.yml", \
  "--storage.tsdb.path=/prometheus", \
  "--web.external-url=http://localhost:9090/internal/monitor" \
]
