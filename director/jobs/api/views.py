import os
import logging

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.views import AccountPermissionsMixin, AccountPermissionType
from jobs.models import Job, Queue, Worker, WorkerHeartbeat, Zone
from jobs.api.serializers import (
    JobListSerializer,
    JobCreateSerializer,
    JobRetrieveSerializer,
    JobUpdateSerializer,
    QueueSerializer,
    WorkerSerializer,
    WorkerHeartbeatSerializer,
    ZoneSerializer,
    ZoneCreateSerializer,
)

logger = logging.getLogger(__name__)


class AccountsBrokerView(
    views.APIView, AccountPermissionsMixin,
):
    """
    A view that provides access to an account's own vhost on the broker.

    This is a POC and is not currently used.
    """

    # Configuration

    required_account_permission = AccountPermissionType.MODIFY

    # Views

    def get(self, request: Request, account: int) -> Response:
        """
        Connect to the job broker for the account.

        This endpoint is for self-hosted workers. These need to be
        enabled for the account.

        You may need to include your authentication token in the URL.
        For example, when using [Celery](https://www.celeryproject.org/) in Python:

        ```python
        account = os.environ.get("STENCILA_ACCOUNT")
        token = os.environ.get("STENCILA_TOKEN")
        app = Celery(
            broker="https://{}@hub.stenci.la/api/accounts/{}/jobs/broker".format(
                token, account
            )
        )
        ```
        """
        self.request_permissions_guard(request, pk=account)
        # TODO: Check that the account has self-hosted workers enabled
        # TODO: Authenticate with the RabbitMQ broker and use account's virtual host
        url = "http://account-user:account-password@broker:0000/account-vhost"
        return Response(
            headers={"X-Accel-Redirect": "@jobs-broker", "X-Accel-Redirect-URL": url}
        )


class AccountsZonesViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
    AccountPermissionsMixin,
):
    """
    A view set for zones.

    Zones are always linked to an account. Therefore, this viewset
    should be nested at `/accounts/{id}/zones`.

    Provides basic CRUD for zones. Zones will usually be implicitly
    created from queue names but can also be created / deleted etc here.
    """

    # Configuration

    lookup_field = "name"

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of zones linked to the account.
        """
        return Zone.objects.filter(account=self.kwargs["account"])

    def get_serializer_class(self):
        """
        Override of `GenericAPIView.get_serializer_class`.

        Returns different serializers for different views.
        """
        return ZoneCreateSerializer if self.action == "create" else ZoneSerializer

    # Views

    def list(self, request: Request, account: int) -> Response:
        """
        List the zones linked to the account.

        Returns details for all zones linked to the account.
        """
        self.request_permissions_guard(
            request, pk=account, permission=AccountPermissionType.VIEW
        )

        return super().list(request, account)

    def create(self, request: Request, account: int) -> Response:
        """
        Create a zone linked to the account.

        Returns details for the new zone.
        """
        self.request_permissions_guard(
            request, pk=account, permission=AccountPermissionType.ADMINISTER
        )

        return super().create(request, account)

    def retrieve(self, request: Request, account: int, name: str) -> Response:
        """
        Retrieve details of a zone linked to the account.

        Returns details for the zone.
        """
        self.request_permissions_guard(
            request, pk=account, permission=AccountPermissionType.VIEW
        )

        return super().retrieve(request, account, name)

    def destroy(self, request: Request, account: int, name: str) -> Response:
        """
        Destroy a zone linked to the account.

        Don't worry, no zones will be harmed by this action :)
        It just removes them from the list of available zones
        for the account.
        """
        self.request_permissions_guard(
            request, pk=account, permission=AccountPermissionType.ADMINISTER
        )

        return super().destroy(request, account, name)


class AccountsQueuesViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    AccountPermissionsMixin,
):
    """
    A view set for queues.

    Queues are always linked to zones which are in turn
    linked to an account. This viewset is nested
    under accounts i.e. `/accounts/{id}/queues` because
    access should be restricted to users with
    permissions to the account. To avoid too deep
    nesting, it is not nested under zones.

    It currently only provides `list` and `retrieve`
    actions (creation is done implicitly).
    """

    # Configuration

    lookup_url_kwarg = "queue"
    serializer_class = QueueSerializer
    required_account_permission = AccountPermissionType.VIEW

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of queues linked to the account.
        """
        return Queue.objects.filter(zone__account=self.kwargs["account"])

    # Views

    def list(self, request: Request, account: int) -> Response:
        """
        List the queues linked to the account.

        Returns details for each queue.
        """
        self.request_permissions_guard(request, pk=account)

        return super().list(request, account)

    def retrieve(self, request: Request, account: int, queue: int) -> Response:
        """
        Retrieve details of a queue linked to the account.

        Returns details for the queue.
        """
        self.request_permissions_guard(request, pk=account)

        return super().retrieve(request, account, queue)


class AccountsWorkersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    AccountPermissionsMixin,
):
    """
    A view set for workers.

    It currently only provides `list` and `retrieve`
    actions (creation is done implicitly when a worker
    comes online; there is no deletion).
    """

    # Configuration

    lookup_url_kwarg = "worker"
    serializer_class = WorkerSerializer
    required_account_permission = AccountPermissionType.VIEW

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of workers linked to the account
        (via queues and zones).
        """
        queryset = Worker.objects.filter(
            queues__zone__account=self.kwargs["account"]
        ).distinct()

        active = self.request.query_params.get("active", None)
        if active == "true":
            queryset = queryset.filter(finished__isnull=True)
        elif active == "false":
            queryset = queryset.filter(finished__isnull=False)

        return queryset

    # Views

    def list(self, request: Request, account: int) -> Response:
        """
        List the workers linked to the account.

        Returns details for each worker.
        """
        self.request_permissions_guard(request, pk=account)

        return super().list(request, account)

    def retrieve(self, request: Request, account: int, worker: int) -> Response:
        """
        Retrieve details of a worker linked to the account.

        Returns details for the worker.
        """
        self.request_permissions_guard(request, pk=account)

        return super().retrieve(request, account, worker)


class AccountsWorkersHeartbeatsViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet, AccountPermissionsMixin
):

    # Configuration

    serializer_class = WorkerHeartbeatSerializer
    required_account_permission = AccountPermissionType.VIEW

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of heartbeats for the worker.
        """
        return WorkerHeartbeat.objects.filter(worker=self.kwargs["worker"]).order_by(
            "-time"
        )

    # Views

    def list(self, request: Request, account: int, worker: int):
        """
        List the heartbeats for a worker.

        Returns details for all heartbeats recorded for the worker
        in reverse chronological order (i.e. most recent first)
        """
        self.request_permissions_guard(request, pk=account)
        return super().list(request, account=account, worker=worker)


class WorkersViewSet(viewsets.GenericViewSet):
    """
    It is intended for the `overseer` service.

    Currently this requires that the user is a Stencila
    staff member.
    """

    # Configuration

    permission_classes = [permissions.IsAdminUser]

    # Views

    @action(detail=False, methods=["POST"])
    def online(self, request: Request) -> Response:
        """
        Create a worker instance when a worker comes online.

        Receives event data.
        Returns an empty response.
        """
        event = request.data

        worker = Worker.get_or_create(event, create=True)
        worker.started = timezone.now()

        # Parse the additional details that are collected
        # when a worker comes online
        details = event.get("details", {})

        # The broker virtual_host that the worker is connected
        # to is equal to the account name
        stats = details.get("stats", {})
        account_name = stats["broker"]["virtual_host"]

        queues = details.get("queues", [])
        if queues:
            for queue in queues:
                queue_instance, created = Queue.get_or_create(
                    account_name=account_name, queue_name=queue.get("name"),
                )
                worker.queues.add(queue_instance)
        else:
            logger.warn(
                "Worker appear to not be listening to any queues: {}".format(
                    worker.signature
                )
            )

        worker.save()

        return Response()

    @action(detail=False, methods=["POST"])
    def heartbeat(self, request: Request) -> Response:
        """
        Create a worker heartbeat.

        Receives event data.
        Returns an empty response.
        """
        event = request.data

        worker = Worker.get_or_create(event)
        worker.updated = timezone.now()
        worker.save()

        WorkerHeartbeat.objects.create(
            worker=worker,
            time=timezone.now(),
            clock=event.get("clock", 0),
            active=event.get("active", 0),
            processed=event.get("processed", 0),
            load=event.get("loadavg", []),
        )

        return Response()

    @action(detail=False, methods=["POST"])
    def offline(self, request: Request) -> Response:
        """
        Record that a worker has gone offline.

        Receives event data.
        Returns an empty response.
        """
        event = request.data

        worker = Worker.get_or_create(event)
        worker.finished = timezone.now()
        worker.save()

        return Response()


class JobsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    # Configuration

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        The `partial_update` action requires a staff user (an internal bot),
        others just require authentication.
        """
        return (
            [permissions.IsAdminUser()]
            if self.action == "partial_update"
            else [permissions.IsAuthenticated()]
        )

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of jobs that the user has view access to.
        """
        # TODO: Also include projects where the user has view access
        return Job.objects.filter(creator=self.request.user)

    def get_serializer_class(self):
        """
        Override of `GenericAPIView.get_serializer_class`.

        Returns different serializers for different views.
        """
        try:
            return {
                "list": JobListSerializer,
                "create": JobCreateSerializer,
                "execute": JobCreateSerializer,
                "retrieve": JobRetrieveSerializer,
                "update": JobUpdateSerializer,
                "partial_update": JobUpdateSerializer,
                "cancel": JobRetrieveSerializer,
                "connect": JobRetrieveSerializer,
            }[self.action]
        except KeyError:
            logger.error("No serializer defined for action {}".format(self.action))
            return JobRetrieveSerializer

    # Standard views

    def list(self, request: Request):
        """
        List jobs.

        Returns details for all jobs the user has access to.
        """
        return super().list(request)

    def create(self, request: Request):
        """
        Create a job.

        Dispatches the job to a queue.
        Returns details for the new job.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer.instance.dispatch()

        return super().create(request)

    def partial_update(self, request: Request, pk: int):
        """
        Update a job.

        This action is intended only to be used by the `overseer` service
        for it to update the details of a job based on events
        from the job queue.
        """
        job = self.get_object()
        job.update()

        serializer = self.get_serializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: int):
        """
        Retrieve a job.

        Returns details for the job.
        """
        job = self.get_object()
        job.update()

        serializer = self.get_serializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Shortcut `create` views
    # These allow for the method and parameters to be in the URL

    @action(detail=False, pagination_class=None, methods=["POST"])
    def execute(self, request) -> Response:
        """
        Create an execute job.

        Receives the `node` to execute as the request body.
        Returns the executed `node`.
        """
        serializer = self.get_serializer(
            data={"method": "execute", "params": request.data}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Other views for connecting to and cancelling jobs

    @swagger_auto_schema(request_body=None)
    @action(detail=True, url_path="connect/?(?P<path>.+)?", methods=["GET", "POST"])
    def connect(self, request, pk: int, path: str) -> Response:
        """
        Connect to a job.

        Redirects to the internal URL so that users can
        connect to the job and run methods inside of it,
        Russian doll style.

        This request it proxied through the `router`. This view
        first checks that the user has permission to edit the
        job.
        """
        # TODO: Check that user has edit rights for job
        job = self.get_object()

        if not job.url:
            return Response(
                {"message": "Job is not ready"}, status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if job.ended:
            return Response(
                {"message": "Job has ended"}, status.HTTP_503_SERVICE_UNAVAILABLE
            )

        job.users.add(request.user)

        # Nginx does not accept the ws:// prefix, so in those
        # cases replace with http://
        url = job.url.replace("ws://", "http://")

        return Response(
            headers={
                "X-Accel-Redirect": "@jobs-connect",
                "X-Accel-Redirect-URL": os.path.join(url, path or ""),
            }
        )

    @swagger_auto_schema(request_body=None)
    @action(detail=True, methods=["PATCH"])
    def cancel(self, request, pk: int) -> Response:
        """
        Cancel a job.

        If the job is cancellable, it will be cancelled
        and it's status set to `REVOKED`.
        """
        job = self.get_object()
        job.cancel()

        serializer = self.get_serializer(job)
        return Response(serializer.data)
