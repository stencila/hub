# Custom Redis Dockerfile allowing for seting password from
# an environment variable
# See https://github.com/docker-library/redis/issues/46#issuecomment-211599210

FROM redis:6.2.5

CMD ["sh", "-c", "exec redis-server --requirepass \"$REDIS_PASSWORD\""]
