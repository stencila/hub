# Stencila Hub Broker

### Role

The `broker` is the mediator between clients, such as the `director` and `scheduler`, and `worker`s. To initiate a task, a client sends a message to the `broker`'s queue, which the `broker` then delivers to a `worker`.

### Solution

We use [Redis](https://redis.io/), a fast, open-source, in-memory key-value data store. The `stencila/hub-broker` Docker image is currently just a simple `FROM redis` image.

Instead of self hosting `stencila/hub-broker` you could use one of the several Redis-as-a-service services, including https://redislabs.com/ from the creators of Redis.

### Alternatives

Celery [supports several brokers](https://docs.celeryproject.org/en/latest/getting-started/brokers/index.html). It should be fairly straightforward to swap out Redis for RabbitMQ if that's what you prefer.

We may use RabbitMQ in the future because it allows for [multi-tenancy via virtual hosts](https://www.rabbitmq.com/vhosts.html). This could be used to allow accounts to provide their own workers by connecting to their own broker `vhost`.
