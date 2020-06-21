# Stencila Hub Broker

## Purpose

The `broker` is the mediator between task producers, such as the `manager`, and `worker`s, the task consumers. To initiate a task, a producer sends a message to the `broker`'s queue, which the `broker` then delivers to a `worker`.

## Solution

We use RabbitMQ because it allows for [multi-tenancy via virtual hosts](https://www.rabbitmq.com/vhosts.html). This allows accounts to provide their own    workers by connecting to their own `vhost` on the broker.

The `stencila/hub-broker` Docker image is currently just a simple `FROM rabbitmq:3.8-management` image. We use the management image, so that we can access the [Management HTTP API](https://www.rabbitmq.com/management.html#http-api) to add new users and vhosts for accounts.

Instead of self hosting `stencila/hub-broker` a RabbitMQ-as-a-service service, such as https://www.cloudamqp.com/ could be used.

## Alternatives

Celery [supports several brokers](https://docs.celeryproject.org/en/latest/getting-started/brokers/index.html). Initially we used [Redis](https://redis.io/) because of it's ease of setup.
