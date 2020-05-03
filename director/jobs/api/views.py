import os
import logging

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.views import Account, AccountPermissionsMixin, AccountPermissionType
from jobs.models import Job, Worker, WorkerStatus, Zone
from jobs.api.serializers import (
    JobListSerializer,
    JobCreateSerializer,
    JobRetrieveSerializer,
    JobUpdateSerializer,
    WorkerSerializer,
    WorkerStatusSerializer,
    ZoneSerializer,
    ZoneCreateSerializer,
)
from jobs import jobs

logger = logging.getLogger(__name__)


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

    def check_object_permissions(self, request: Request, job: Job):
        """
        Override of `APIView.check_object_permissions`.

        Checks that the user is either the creator of the job,
        or has view access to the project.
        """
        # TODO: Also permit users with view access to the project
        if request.user != job.creator:
            raise PermissionDenied

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

        Returns details for the new job.
        """
        return super().create(request)

    def partial_update(self, request: Request, pk: int):
        """
        Update a job.

        This action is only available to the `overseer` service
        for it to update the details of a job based on events
        from the job queue.
        """
        job = jobs.update(self.get_object())
        serializer = self.get_serializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: int):
        """
        Retrieve a job.

        Returns details for the job.
        """
        job = jobs.update(self.get_object())
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
        job = jobs.cancel(self.get_object())
        serializer = self.get_serializer(job)
        return Response(serializer.data)


class AccountsJobsViewSet(viewsets.GenericViewSet):
    """
    A view set for jobs linked to an account.

    Currently, this view set just provides access to the job broker
    for an account. In the future it may allow for listing of jobs
    by account ie. `GET /accounts/{id}/jobs`.
    """

    # Configuration

    serializer_class = None

    # Views

    @swagger_auto_schema()
    @action(
        detail=False,
        permission_classes=[permissions.IsAdminUser],
        pagination_class=None,
    )
    def broker(self, request, pk: int) -> Response:
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

        Currently, this endpoint is restricted to Stencila staff pending
        implementation of multi-tenancy in the broker.
        """
        # TODO: Get or 404 the account
        # TODO: Check that the user has sufficient account permissions
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
    should be available at `/accounts/{id}/zones`.
    It provides basic CRUD for zones.
    """

    # Configuration

    lookup_field = "name"

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of zones linked to the account.
        """
        return Zone.objects.filter(account=self.kwargs["pk"])

    def get_serializer_class(self):
        """
        Override of `GenericAPIView.get_serializer_class`.

        Returns different serializers for different views.
        """
        return ZoneCreateSerializer if self.action == "create" else ZoneSerializer

    # Views

    def list(self, request: Request, pk: int):
        """
        List the zones linked to the account.

        Returns details for all zones linked to the account.
        """
        # TODO: Check that user is an account member

        return super().list(request, pk)

    def create(self, request: Request, pk: int):
        """
        Create a zone linked to the account.

        Returns details for the new zone.
        """
        # TODO: Replace with shortcut `is_permitted` method
        self.perform_account_fetch(self.request.user, Account.objects.get(id=pk).name)
        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        return super().create(request, pk)

    def retrieve(self, request: Request, pk: int, name: str):
        """
        Retrieve details of a zone linked to the account.

        Returns details for the zone.
        """
        # TODO: Check that user is an account member

        return super().retrieve(request, pk, name)

    def destroy(self, request: Request, pk: int, name: str):
        """
        Destroy a zone linked to the account.

        Don't worry, no zones will be harmed by this action :)
        It just removes them from the list of available zones
        for the account.
        """
        # TODO: Replace with shortcut `is_permitted` method
        self.perform_account_fetch(self.request.user, Account.objects.get(id=pk).name)
        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        return super().destroy(request, pk, name)


class WorkersViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):

    # Configuration

    serializer_class = WorkerSerializer

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of workers that the user has view access to.
        """
        # TODO: Should only list workers in zones the user has access to
        return Worker.objects.all()

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        The `events` action requires a staff user (an internal bot),
        others just require authentication.
        """
        return (
            [permissions.IsAdminUser()]
            if self.action == "events"
            else [permissions.IsAuthenticated()]
        )

    # Views

    def list(self, request: Request):
        """
        List workers.

        Returns details for all workers the user has access to.
        """
        return super().list(request)

    def retrieve(self, request: Request, pk: int):
        """
        Retrieve a worker.

        Returns details for the worker.
        """
        return super().retrieve(request, pk)

    @action(detail=False, methods=["POST"])
    def events(self, request) -> Response:
        """
        Submit a worker event.

        Depending upon the `type` of the event, this will:

        - worker-online: create a new worker
        - worker-heartbeat: update the status of an existing worker
        - worker-offline: mark a worker as inactive
        """
        event = request.data

        event_type = event.get("type")
        hostname = event.get("hostname")
        utcoffset = event.get("utcoffset")
        pid = event.get("pid")
        freq = event.get("freq")
        software = "{}-{}".format(event.get("sw_ident"), event.get("sw_ver"))
        os = event.get("sw_sys")

        # Generate signature and check for an active worker with that signature
        signature = "{hostname}|{utcoffset}|{pid}|{freq}|{software}|{os}".format(
            hostname=hostname,
            utcoffset=utcoffset,
            pid=pid,
            freq=freq,
            software=software,
            os=os,
        )
        try:
            worker = Worker.objects.get(signature=signature, finished__isnull=True)
        except Worker.DoesNotExist:
            worker = Worker.objects.create(
                hostname=hostname,
                utcoffset=utcoffset,
                pid=pid,
                freq=freq,
                software=software,
                os=os,
                signature=signature,
            )

        if event_type == "worker-online":
            worker.started = timezone.now()
        elif event_type == "worker-heartbeat":
            worker.updated = timezone.now()
        elif event_type == "worker-offline":
            worker.finished = timezone.now()
        worker.save()

        WorkerStatus.objects.create(
            worker=worker,
            time=timezone.now(),
            clock=event.get("clock", 0),
            active=event.get("active", 0),
            processed=event.get("processed", 0),
            load=event.get("loadavg", []),
        )

        serializer = self.get_serializer(worker)
        return Response(serializer.data)


class WorkersStatusesViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet,
):

    # Configuration

    serializer_class = WorkerStatusSerializer

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the list of statuses linked to the worker.
        """
        return WorkerStatus.objects.filter(worker=self.kwargs["pk"]).order_by("-time")

    # Views

    def list(self, request: Request, pk: int):
        """
        List the status reports for a worker.

        Returns details for all status report for the worker
        in reverse chronological order (i.e. most recent first)
        """
        return super().list(request, pk)
