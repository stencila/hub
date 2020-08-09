import logging
import os
import random
import secrets
import subprocess
import sys
import time

import kubernetes

from jobs.base.job import Job

# Kubernetes namespace to put job pods in
namespace = "jobs"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if "--debug" in sys.argv else logging.INFO)

api_client = None
if "KUBERNETES_SERVICE_HOST" in os.environ:
    # Running in a pod on the cluster so load the cluster's config
    kubernetes.config.load_incluster_config()
    api_instance = kubernetes.client.CoreV1Api()
else:
    # Running outside of a cluster, probably during development
    if __name__ == "__main__":
        # Explicitly running this script so connect to active cluster
        api_client = kubernetes.config.new_client_from_config()
        api_instance = kubernetes.client.CoreV1Api(api_client)
    else:
        # Otherwise only connect to a Minikube cluster to avoid polluting
        # a production cluster accidentally.
        # Do not raise an exception so that devs without Minikube
        # installed can at least import this file. Just warn.
        api_instance = None
        try:
            status = subprocess.run(["minikube", "status"])
            if status.returncode == 0:
                try:
                    api_client = kubernetes.config.new_client_from_config(
                        context="minikube"
                    )
                    api_instance = kubernetes.client.CoreV1Api(api_client)

                    try:
                        # Create the job namespace. In production, this namespace
                        # needs to be created manually.
                        api_instance.create_namespace(
                            body={
                                "apiVersion": "v1",
                                "kind": "Namespace",
                                "metadata": {"name": namespace},
                            }
                        )
                    except kubernetes.client.rest.ApiException:
                        # Assume that exception was because namespace already exists
                        pass
                except kubernetes.config.config_exception.ConfigException as exc:
                    logger.warning(exc)
            else:
                logger.warning(
                    "Minikube does not appear to be running. Run: minikube start"
                )
        except FileNotFoundError:
            logger.warning("Could not find Minikube. Is it installed?")


class KubernetesSession(Job):
    """
    Runs a session as a pod in a Kubernetes cluster.

    This class in intended for scalably provisioning
    untrusted sessions. It uses the K8s API to create
    a new pod inside a cluster, possible the same cluster
    this process is in.
    """

    def do(self, *args, **kwargs):
        """
        Start the session.

        Override of `Job.do` which updates the job state with the
        URL of the session before starting the session (which blocks
        until the job is terminated).
        """
        # Get session parameters, with warning, errors or
        # exceptions if they are not present
        key = kwargs.get("key")
        assert key is not None, "A job key is required for a session"

        environ = kwargs.get("environ")
        if environ is None:
            environ = "stencila/executa"
            logger.warning("Using default environment")

        # Use short timeout and timelimit defaults
        timeout = kwargs.get("timeout", 15 * 60)
        timelimit = kwargs.get("timelimit", 60 * 60)

        # Update the job with a custom state to indicate
        # that we are waiting for the pod to start.
        self.notify(state="LAUNCHING")

        # Create a session name which we can use to terminate the pod
        # (use `pod_name` to avoid clash with `Job.name`)
        self.pod_name = "session-" + (self.task_id or secrets.token_hex(16))

        # Add pod name to logger's extra contextual info
        self.logger = logging.LoggerAdapter(logger, {"pod_name": self.pod_name})

        # Create pod listening on a random port number
        protocol = "ws"
        port = random.randint(10000, 65535)
        self.logger.debug("Creating pod")
        api_instance.create_namespaced_pod(
            body={
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": self.pod_name, "app": "session"},
                "spec": {
                    "containers": [
                        {
                            "name": "executa",
                            "image": environ,
                            "args": [
                                "executa",
                                "serve",
                                "--debug",
                                "--{}=0.0.0.0:{}".format(protocol, port),
                                "--key={}".format(key),
                                "--timeout={}".format(timeout),
                                "--timelimit={}".format(timelimit),
                            ],
                            "ports": [{"containerPort": port}],
                        }
                    ],
                    "restartPolicy": "Never",
                },
            },
            namespace=namespace,
        )

        # Wait for pod to be ready so that we can get its IP address
        self.logger.debug("Waiting for pod")
        while True:
            pod = api_instance.read_namespaced_pod(
                name=self.pod_name, namespace=namespace
            )
            if pod.status.phase != "Pending":
                break
            time.sleep(0.25)
        ip = pod.status.pod_ip

        # Update the job state with the internal URL of the pod
        self.notify(state="RUNNING", url="{}://{}:{}".format(protocol, ip, port))

        self.logger.debug("Started pod")

        # Stream pod's stdout and stderr to here
        try:
            response = kubernetes.stream.stream(
                api_instance.connect_get_namespaced_pod_attach,
                name=self.pod_name,
                namespace=namespace,
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
                stderr = response.readline_stderr(timeout=3)
                print(stderr)
        except kubernetes.client.rest.ApiException as exc:
            # Log the exception if it is not an expected
            # SoftTimeLimitExceeded exception (used for cancelling
            # / terminating jobs)
            if "SoftTimeLimitExceeded" not in exc.reason:
                logger.exception(exc)
            # Always terminate the pod if there has been an exception
            return self.terminated()

        self.logger.info("Pod finished")

    def terminated(self):
        """
        Stop the session.
        """
        if self.pod_name:
            self.logger.info("Terminating pod")
            api_instance.delete_namespaced_pod(name=self.pod_name, namespace=namespace)
            self.pod_name = None


if __name__ == "__main__":
    import secrets

    session = KubernetesSession()
    session.run(key=secrets.token_urlsafe(8))
