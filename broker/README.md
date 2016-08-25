# Broker

The `broker` role supports realtime collaboration sessions on Stencila components. It consists of a Node.js server (see `broker.js`) backed by a Redis database (see `redis.conf`).

The `supervisord.conf` is set up so that everything runs, logs and, in the case of Redis saves snapshots (to `dump.rdb`) into this directory. So you'll need to `mkdir logs` first.
