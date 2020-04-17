#!/usr/bin/env sh

# Docker ENTRYPOINT script to use `envsubst` to insert environment variables
# into the Nginx config.
# Thanks to https://serverfault.com/a/919212

set -eu

: "${DIRECTOR_URL:?Env var DIRECTOR_URL must be set and non-empty}"
: "${BROKER_URL:?Env var BROKER_URL must be set and non-empty}"

envsubst '${DIRECTOR_URL} ${BROKER_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

exec "$@"
