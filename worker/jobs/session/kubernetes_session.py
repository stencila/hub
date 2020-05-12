"""
Module that defines the `KubernetesSession` class.
"""

import logging
import os
import random
import secrets
import time

import kubernetes

from .session import Session


logger = logging.getLogger(__name__)


api_client = None
if "KUBERNETES_SERVICE_HOST" in os.environ:
    # Running in a pod on the cluster so load the cluster's config
    kubernetes.config.load_incluster_config()
    api_client = kubernetes.client.CoreV1Api()
else:
    # Running outside of a cluster, probably during development
    # so only connect to a Minikube cluster to avoid polluting
    # a production cluster accidentally.
    # Do not raise an exception so that devs without Minikube
    # installed can at least import this file. Just warn.
    try:
        api_client = kubernetes.config.new_client_from_config(context="minikube")
    except kubernetes.config.config_exception.ConfigException as exc:
        logger.warning(exc)


class KubernetesSession(Session):
    """
    Runs a session as a pod in a Kubernetes cluster.

    This class in intended for scalably provisioning
    untrusted sessions. It uses the K8s API to create
    a new pod inside a cluster, possible the same cluster
    this process is in.
    """

    api_instance = kubernetes.client.CoreV1Api(api_client) if api_client else None
    namespace = "default"

    def __init__(self):
        """Create a session."""
        super().__init__()
        self.name = "session-" + secrets.token_hex(16)
        self.port = random.randint(1024, 65535)

        self.api_instance.create_namespaced_pod(
            body={
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": self.name},
                "spec": {
                    "containers": [
                        {
                            "name": "executa",
                            "image": "stencila/executa",
                            "args": [
                                "executa",
                                "serve",
                                "--debug",
                                "--{}=0.0.0.0:{}".format(self.protocol, self.port),
                            ],
                        }
                    ],
                    "restartPolicy": "Never",
                },
            },
            namespace=self.namespace,
        )

        while True:
            pod = self.api_instance.read_namespaced_pod(
                name=self.name, namespace=self.namespace
            )
            if pod.status.phase != "Pending":
                break
            time.sleep(0.1)

        self.ip = pod.status.pod_ip

    def start(self):
        """Start the session."""
        return

        response = kubernetes.stream.stream(
            self.api_instance.connect_get_namespaced_pod_attach,
            name=self.name,
            namespace=self.namespace,
            container="executa",
            stderr=True,
            stdout=True,
            stdin=False,
            tty=False,
        )
        while response.is_open():
            response.update(timeout=1)
            stdout = response.readline_stdout(timeout=3)
            print(stdout)

    def stop(self):
        """Stop the session."""
        super().stop()
        if self.name:
            self.api_instance.delete_namespaced_pod(
                name=self.name, namespace=self.namespace
            )
            self.name = None
