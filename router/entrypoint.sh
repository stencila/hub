#!/usr/bin/env sh

# Docker ENTRYPOINT script to use `envsubst` to insert environment variables
# into the Nginx config.
# Thanks to https://serverfault.com/a/919212

set -eu

: "${MANAGER_HOST:?Env var MANAGER_HOST must be set and non-empty}"
: "${MONITOR_URL:?Env var MONITOR_URL must be set and non-empty}"

envsubst '${MANAGER_HOST} ${MONITOR_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

exec "$@"
