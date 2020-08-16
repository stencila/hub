#!/usr/bin/env sh

set -eu

# Increase the number of worker connections from the
# default of 1024 to avoid the warning "1024 worker_connections are not enough, reusing connections"
# observed during stress testing.
# Needs to be set in /etc/nginx/nginx.conf, not our /etc/nginx/conf.d/default.conf
# See https://craftypixels.com/worker-connections-are-not-enough/
sed -i -e "s/worker_connections  1024/worker_connections  2048/g" /etc/nginx/nginx.conf

# Use `envsubst` to insert environment variables into the Nginx config.
# Thanks to https://serverfault.com/a/919212

: "${MANAGER_HOST:?Env var MANAGER_HOST must be set and non-empty}"
: "${MONITOR_URL:?Env var MONITOR_URL must be set and non-empty}"
: "${RESOLVER_ADDRESS:?Env var RESOLVER_ADDRESS must be set and non-empty}"

envsubst '${MANAGER_HOST} ${MONITOR_URL} ${RESOLVER_ADDRESS}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

exec "$@"
