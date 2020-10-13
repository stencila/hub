import logging
import os
import random
import secrets
import subprocess
import sys
import time

from celery.exceptions import Ignore, SoftTimeLimitExceeded
import kubernetes

from config import get_snapshot_dir, get_working_dir
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

    This class in intended for scalably provisioning untrusted sessions.
    It uses the K8s API to create a new pod inside a cluster, usually but
    not necessarily, the same cluster this process is in.
    """

    def do(self, *args, **kwargs):
        """
        Start the session.

        Override of `Job.do` which updates the job state with the
        URL of the session before starting the session.
        """
        # Get session parameters, falling back to defaults either set
        # as environment variables or the values hard coded below.

        # Project to start session for
        project = kwargs.get("project")
        assert project is not None, "A project id is required to start a session"

        # Snapshot to start session for (if any)
        snapshot = kwargs.get("snapshot")

        # Key to control access to the session
        key = kwargs.get("key")
        assert key is not None, "A job key is required for a session"

        # Container image to use
        container_image = kwargs.get("container_image") or os.getenv(
            "SESSION_CONTAINER_IMAGE", "stencila/executa-midi"
        )

        # Session timeout and timelimit defaults
        timeout = kwargs.get("timeout") or os.getenv(
            "SESSION_TIMEOUT_DEFAULT", 600  # 10 minutes
        )
        timelimit = kwargs.get("timelimit") or os.getenv(
            "SESSION_TIMELIMIT_DEFAULT", 3600  # 1 hour
        )

        # Node pool
        node_pool = kwargs.get("node_pool") or os.getenv(
            "SESSION_NODE_POOL_DEFAULT", "sessions"
        )

        # Session CPU and memory requests and limits
        cpu_request = kwargs.get("cpu_request") or os.getenv(
            "SESSION_CPU_REQUEST_DEFAULT", 0.1  # 10% of a vCPU / core
        )
        cpu_limit = kwargs.get("cpu_limit") or os.getenv(
            "SESSION_CPU_LIMIT_DEFAULT", 1  # 100% of a vCPU / core
        )
        mem_request = kwargs.get("mem_request") or os.getenv(
            "SESSION_MEM_REQUEST_DEFAULT", 600  # 600MiB
        )
        mem_limit = kwargs.get("mem_limit") or os.getenv(
            "SESSION_MEM_LIMIT_DEFAULT", 600  # 600MiB
        )

        # Network policy applied to sessions
        network_policy = kwargs.get("network_policy") or os.getenv(
            "SESSION_NETWORK_POLICY_DEFAULT", "jobs-network-policy-1"
        )

        # Update the job with a custom state to indicate
        # that we are waiting for the pod to start.
        self.notify(state="LAUNCHING")

        # Create a session name which we can use to terminate the pod
        # (use `pod_name` to avoid clash with `Job.name`)
        self.pod_name = "session-" + (self.task_id or secrets.token_hex(16))

        # Add pod name to logger's extra contextual info
        self.logger = logging.LoggerAdapter(logger, {"pod_name": self.pod_name})

        # Determine the path on the host for the session's working directory
        host_path = "/var/lib/stencila/hub/storage"
        workdir = (
            os.path.join(host_path, "snapshots", str(project), snapshot)
            if snapshot
            else os.path.join(host_path, "working", str(project))
        )

        # Create pod listening on a random port number
        protocol = "ws"
        port = random.randint(10000, 65535)
        pod = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": self.pod_name,
                "labels": {"method": "session", "networkPolicy": network_policy},
            },
            "spec": {
                "nodeSelector": {"cloud.google.com/gke-nodepool": node_pool},
                "containers": [
                    {
                        "name": "session",
                        "image": container_image,
                        "command": [
                            "executa",
                            "serve",
                            "--{}=0.0.0.0:{}".format(protocol, port),
                            "--key={}".format(key),
                            "--timeout={}".format(timeout),
                            "--timelimit={}".format(timelimit),
                        ],
                        "securityContext": {"runAsUser": 1000, "runAsGroup": 1000},
                        "ports": [{"containerPort": port}],
                        "readinessProbe": {
                            "tcpSocket": {"port": port},
                            "initialDelaySeconds": 2,
                            "periodSeconds": 1,
                            "failureThreshold": 60,
                        },
                        "volumeMounts": [
                            {
                                "name": "work",
                                "mountPath": "/work",
                                "mountPropagation": "HostToContainer",
                            }
                        ],
                        "workingDir": "/work",
                        "resources": {
                            "requests": {
                                "cpu": cpu_request,
                                "memory": "{}Mi".format(mem_request),
                            },
                            "limits": {
                                "cpu": cpu_limit,
                                "memory": "{}Mi".format(mem_limit),
                            },
                        },
                    },
                    {
                        # Container which provides readonly access to the project or snapshot directory
                        # while still allowing the session to write to the working directory.
                        # This is done in a separate sidecar container to avoid having the session
                        # container be privileged.
                        "name": "mounter",
                        "image": "ubuntu:20.04",
                        "securityContext": {"privileged": True},
                        # Create an overlay mount with the data directory as the lower directory
                        # The `tail` makes this container, and thus the mount, run forever.
                        "command": ["/bin/bash", "-c", "--"],
                        "args": [
                            """
                           mkdir -p /overlay/{upper,work}
                           mount -t overlay overlay \
                                 -o lowerdir=/data,upperdir=/overlay/upper,workdir=/overlay/work \
                                 /work
                           chown 1000:1000 /work
                           tail -f /dev/null
                           """
                        ],
                        # Unmount otherwise this container will never terminate.
                        "lifecycle": {
                            "preStop": {"exec": {"command": ["umount", "/work"]}}
                        },
                        "volumeMounts": [
                            # Read only data directory (snapshot or project working directory)
                            {"name": "data", "mountPath": "/data", "readOnly": True},
                            # Temporary working directory for overlay mount to use
                            {"name": "overlay", "mountPath": "/overlay"},
                            # Bidirectional mount allowing the session container
                            # to mount the /work directory
                            {
                                "name": "work",
                                "mountPath": "/work",
                                "mountPropagation": "Bidirectional",
                            },
                        ],
                    },
                ],
                "volumes": [
                    {"name": "data", "hostPath": {"path": workdir}},
                    {"name": "overlay", "emptyDir": {}},
                    {"name": "work", "emptyDir": {}},
                ],
                # Do not restart this pod when it stops
                "restartPolicy": "Never",
                # Do not automatically mount a token for K8s API access
                "automountServiceAccountToken": False,
            },
        }

        # Try to create the pod, but it it already exists then ignore
        # the job (do not record any state from here but remove it from the queue).
        # See https://docs.celeryproject.org/en/latest/userguide/tasks.html#ignore
        try:
            self.logger.debug("Creating pod")
            api_instance.create_namespaced_pod(
                body=pod, namespace=namespace,
            )
        except kubernetes.client.rest.ApiException as exc:
            if exc.reason == "Conflict":
                raise Ignore()
            else:
                raise exc

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

        try:
            self.poll()
        except (SoftTimeLimitExceeded, KeyboardInterrupt):
            return self.terminated()
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

    def attach(self):
        """
        Attach to the pod's stdout and stderr streams.
        """
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
                self.info(stdout)
                stderr = response.readline_stderr(timeout=3)
                self.info(stderr)
        else:
            self.info(response)

    def poll(self):
        """
        Poll the session until it stops running.
        """
        while True:
            pod = api_instance.read_namespaced_pod(
                name=self.pod_name, namespace=namespace
            )
            if pod.status.phase != "Running":
                return
            time.sleep(3)

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
    parser.add_argument("--project", type=int, help="Project the session is for (id)")
    parser.add_argument(
        "--snapshot", default=None, type=str, help="Snapshot the session is for (id)"
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
        "--network-policy",
        default=None,
        type=str,
        help="Network policy to apply to the pod",
    )
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    session = KubernetesSession()
    session.run(
        project=args.project,
        snapshot=args.snapshot,
        key=secrets.token_urlsafe(8),
        timeout=args.timeout,
        timelimit=args.timelimit,
        network_policy=args.network_policy,
    )
