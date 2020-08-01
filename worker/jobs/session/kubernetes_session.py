import logging
import os
import random
import secrets
import sys
import time

import kubernetes

from jobs.base.job import Job


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


class KubernetesSession(Job):
    """
    Runs a session as a pod in a Kubernetes cluster.

    This class in intended for scalably provisioning
    untrusted sessions. It uses the K8s API to create
    a new pod inside a cluster, possible the same cluster
    this process is in.
    """

    api_instance = kubernetes.client.CoreV1Api(api_client) if api_client else None
    namespace = "default"

    def do(self, *args, **kwargs):
        """
        Start the session.

        Override of `Job.do` which updates the job state with the
        URL of the session before starting the session (which blocks
        until the job is terminated).
        """
        # Update the job with a custom state to indicate
        # that we are waiting for the pod to start.
        self.notify(state="LAUNCHING")

        # Create a session name which we can use to terminate the pod
        self.name = "job-" + (self.task_id or secrets.token_hex(16))

        # Create pod listening on a random port number
        protocol = "ws"
        port = random.randint(10000, 65535)
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
                                "--{}=0.0.0.0:{}".format(protocol, port),
                            ],
                        }
                    ],
                    "restartPolicy": "Never",
                },
            },
            namespace=self.namespace,
        )

        # Wait for pod to be ready so that we can get its IP address
        while True:
            pod = self.api_instance.read_namespaced_pod(
                name=self.name, namespace=self.namespace
            )
            if pod.status.phase != "Pending":
                break
            time.sleep(0.25)
        ip = pod.status.pod_ip

        # Update the job state with the internal URL of the pod
        self.notify(state="RUNNING", url="{}://{}:{}".format(protocol, ip, port))

        # Stream pod's stdout and stderr to here
        try:
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
        except kubernetes.client.rest.ApiException:
            self.terminated()

    def terminated(self):
        """
        Stop the session.
        """
        if self.name:
            self.api_instance.delete_namespaced_pod(
                name=self.name, namespace=self.namespace
            )
            self.name = None
