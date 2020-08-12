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
            environ = "stencila/executa-midi"
            logger.warning("Using default environment")

        # The snapshot directory to use as the working directory
        # for the session
        snapshot_path = kwargs.get("snapshot_path")

        # Use short timeout and timelimit defaults
        timeout = kwargs.get("timeout") or (10 * 60)
        timelimit = kwargs.get("timelimit") or (60 * 60)

        # Update the job with a custom state to indicate
        # that we are waiting for the pod to start.
        self.notify(state="LAUNCHING")

        # Create a session name which we can use to terminate the pod
        # (use `pod_name` to avoid clash with `Job.name`)
        self.pod_name = "session-" + (self.task_id or secrets.token_hex(16))

        # Add pod name to logger's extra contextual info
        self.logger = logging.LoggerAdapter(logger, {"pod_name": self.pod_name})

        if snapshot_path:
            init_script = """
if [ ! -d /snapshots/{id} ]; then
    mkdir -p /snapshots/{id}
    gsutil -m cp -r gs://stencila-hub-snapshots/{id} /snapshots/{id}
fi
            """.format(
                id=snapshot_path
            )
            init_containers = [
                {
                    "name": "init",
                    "image": "gcr.io/google.com/cloudsdktool/cloud-sdk:alpine",
                    "command": ["sh", "-c", init_script],
                    "volumeMounts": [{"name": "snapshots", "mountPath": "/snapshots"}],
                    "env": [
                        {
                            "name": "GOOGLE_APPLICATION_CREDENTIALS",
                            "value": "/secrets/gcloud-service-account-credentials.json",
                        }
                    ],
                }
            ]
            volume_mounts = [
                {
                    "name": "snapshots",
                    # Only mount the directory for the specific snapshot so that
                    # the container does not have access to other snapshots.
                    "subPath": snapshot_path,
                    "readOnly": True,
                    # The path that the snapshot directory is mounted *into*
                    "mountPath": "/snapshots/" + os.path.dirname(snapshot_path),
                }
            ]
            working_dir = "/snapshots/" + snapshot_path
        else:
            init_containers = []
            volume_mounts = []
            working_dir = None

        # Create pod listening on a random port number
        protocol = "ws"
        port = random.randint(10000, 65535)
        self.logger.debug("Creating pod")
        api_instance.create_namespaced_pod(
            body={
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {
                    "name": self.pod_name,
                    "labels": {
                        "method": "session",
                        # Currently not applying this label because network
                        # egress is necessary for the init container
                        # This may become a separate service which is allowed in the
                        # network policy.
                        # "networkPolicy": "egress-denied"
                    },
                },
                "spec": {
                    "initContainers": init_containers,
                    "containers": [
                        {
                            "name": "executa",
                            "image": environ,
                            "command": [
                                "executa",
                                "serve",
                                "--debug",
                                "--{}=0.0.0.0:{}".format(protocol, port),
                                "--key={}".format(key),
                                "--timeout={}".format(timeout),
                                "--timelimit={}".format(timelimit),
                            ],
                            "ports": [{"containerPort": port}],
                            "readinessProbe": {
                                "tcpSocket": {"port": port},
                                "initialDelaySeconds": 0,
                                "periodSeconds": 1,
                                "failureThreshold": 60,
                            },
                            "volumeMounts": volume_mounts,
                            "workingDir": working_dir,
                        }
                    ],
                    "volumes": [
                        {
                            # Snapshots stored on the host and obtained by the
                            # initcontainer
                            "name": "snapshots",
                            "hostPath": {
                                "path": "/var/lib/stencila/snapshots",
                                "type": "DirectoryOrCreate",
                            },
                        },
                        {
                            # Secrets needed by the initcontainer to fetch snapshots
                            "name": "secrets",
                            "secret": {"secretName": "secrets"},
                        },
                    ],
                    # Do not restart this pod when it stops
                    "restartPolicy": "Never",
                    # Do not automatically mount a token for K8s API access
                    "automountServiceAccountToken": False,
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
            # Check readiness of the container
            # The Python API `V1ContainerStatus` does not expose `started`
            # so we use `ready` and a `readinessProbe` (above).
            phase = pod.status.phase
            ready = (
                pod.status.container_statuses
                and len(pod.status.container_statuses)
                and pod.status.container_statuses[0].ready
                or False
            )
            if phase == "Running" and ready:
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
            if hasattr(response, "is_open"):
                while response.is_open():
                    response.update(timeout=1)
                    stdout = response.readline_stdout(timeout=3)
                    print(stdout)
                    stderr = response.readline_stderr(timeout=3)
                    print(stderr)
            else:
                print(response)
        except kubernetes.client.rest.ApiException as exc:
            # Log the exception if it is not an expected
            # SoftTimeLimitExceeded exception (used for cancelling
            # / terminating jobs)
            if "SoftTimeLimitExceeded" not in exc.reason:
                logger.exception(exc)
            # Always terminate the pod if there has been an exception
            return self.terminated()

        self.logger.info("Pod finished")
        return self.completed()

    def terminated(self):
        """
        Stop the session.
        """
        if self.pod_name:
            self.logger.info("Terminating pod")
            api_instance.delete_namespaced_pod(name=self.pod_name, namespace=namespace)
            self.pod_name = None

    def completed(self):
        """
        Clean up the pod if the pod completed i.e. timeout or timelimit

        If we do not do this clean up then these finished pods just end up
        polluting the namespace.
        """
        if self.pod_name:
            self.logger.info("Deleting pod")
            api_instance.delete_namespaced_pod(name=self.pod_name, namespace=namespace)
            self.pod_name = None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", default=False, type=bool, help="Output debug log entries"
    )
    parser.add_argument(
        "--timeout",
        default=None,
        type=int,
        help="Durations of inactivity until session times out (s)",
    )
    parser.add_argument(
        "--timelimit", default=None, type=int, help="Maximum time limit (s)",
    )
    parser.add_argument(
        "--snapshot", default=None, type=str, help="Snapshot to use for /work directory"
    )
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    session = KubernetesSession()
    session.run(
        key=secrets.token_urlsafe(8),
        timeout=args.timeout,
        timelimit=args.timelimit,
        snapshot_path=args.snapshot,
    )
