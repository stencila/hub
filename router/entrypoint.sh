#!/usr/bin/env sh

set -eu

# Use `envsubst` to insert environment variables into the Nginx config.
# Thanks to https://serverfault.com/a/919212

: "${MANAGER_HOST:?Env var MANAGER_HOST must be set and non-empty}"
: "${MONITOR_URL:?Env var MONITOR_URL must be set and non-empty}"
: "${RESOLVER_ADDRESS:?Env var RESOLVER_ADDRESS must be set and non-empty}"

envsubst '${MANAGER_HOST} ${MONITOR_URL} ${RESOLVER_ADDRESS}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

exec "$@"
