import logging
import os
import re
from typing import List, Optional

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    exceptions,
    mixins,
    permissions,
    status,
    throttling,
    views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.api.views import get_account
from accounts.models import AccountRole
from jobs.api.serializers import (
    JobCreateSerializer,
    JobListSerializer,
    JobRetrieveSerializer,
    JobUpdateSerializer,
    QueueSerializer,
    WorkerHeartbeatSerializer,
    WorkerSerializer,
    ZoneCreateSerializer,
    ZoneSerializer,
)
from jobs.models import Job, Queue, Worker, WorkerHeartbeat, Zone
from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxDestroyMixin,
    HtmxListMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    filter_from_ident,
)
from projects.api.views.projects import get_project
from projects.models.projects import Project, ProjectRole

logger = logging.getLogger(__name__)


class AccountsBrokerView(views.APIView):
    """
    A view that provides access to an account's own vhost on the broker.

    This is a POC and is not currently used.
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        """
        Connect to the job broker for the account.

        This endpoint is for self-hosted workers. These need to be
        enabled for the account.

        You may need to include your authentication token in the URL.
        For example, when using [Celery](https://www.celeryproject.org/) in Python:

        ```python
        app = Celery(
            broker="https://{token}@hub.stenci.la/api/accounts/{account}/jobs/broker".format(
                token = os.environ.get("STENCILA_TOKEN"),
                account = os.environ.get("STENCILA_ACCOUNT")
            )
        )
        ```
        """
        get_account(kwargs["account"], request.user)

        # TODO: Check that the account has self-hosted workers enabled
        # TODO: Authenticate with the RabbitMQ broker and use account's virtual host
        url = "http://account-user:account-password@broker:0000/account-vhost"
        return Response(
            headers={"X-Accel-Redirect": "@jobs-broker", "X-Accel-Redirect-URL": url}
        )


class AccountsZonesViewSet(
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxDestroyMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for zones.

    Zones are always linked to an account. Therefore, this viewset
    should be nested at `/accounts/{account}/zones`.

    Provides basic CRUD for zones. Zones will usually be implicitly
    created from queue names but can also be created / deleted etc here.
    """

    lookup_url_kwarg = "zone"
    object_name = "zone"
    queryset_name = "zones"

    def get_queryset(self, roles: Optional[List[AccountRole]] = None):
        """
        Get the queryset for the current action.

        If the user is a member of the account, returns all zones for the account.
        Otherwise, raises permission denied.
        """
        account = get_account(self.kwargs["account"], self.request.user, roles)
        return Zone.objects.filter(account=account)

    def get_object(self):
        """
        Get the object for the current action.

        For `destroy`, ensures that the users is an
        account manager or owner. Otherwise, ensures that the user
        is an account member.
        """
        queryset = self.get_queryset(
            [AccountRole.MANAGER, AccountRole.OWNER]
            if self.action == "destroy"
            else None
        )
        return queryset.get(**filter_from_ident(self.kwargs["zone"]))

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        For `create`, ensures that the users is an
        account manager or owner.
        """
        if self.action == "create":
            # Permission check
            # Skip when doing API Schema generation
            # (permission check should probably go elsewhere)
            if not getattr(self, "swagger_fake_view", False):
                self.get_queryset([AccountRole.MANAGER, AccountRole.OWNER])
            return ZoneCreateSerializer
        else:
            return ZoneSerializer


class AccountsQueuesViewSet(
    HtmxListMixin, HtmxRetrieveMixin, viewsets.GenericViewSet,
):
    """
    A view set for queues.

    Queues are always linked to zones which are in turn
    linked to an account. This viewset is nested
    under accounts i.e. `/accounts/{account}/queues` because
    access should be restricted to users with
    permissions to the account. To avoid too deep
    nesting, it is not nested under zones.

    It currently only provides `list` and `retrieve`
    actions (creation is done implicitly).
    """

    lookup_url_kwarg = "queue"
    object_name = "queue"
    queryset_name = "queues"
    serializer_class = QueueSerializer

    def get_queryset(self):
        """
        Get the queryset for the current action.

        If the user is a member of the account, returns all queues for the account.
        Otherwise, raises permission denied.
        """
        account = get_account(self.kwargs["account"], self.request.user)
        return Queue.objects.filter(zone__account=account)

    def get_object(self):
        """
        Get the object for the current action.

        Ensures that the users is an account member.
        """
        queryset = self.get_queryset()
        return queryset.get(**filter_from_ident(self.kwargs["queue"]))


class AccountsWorkersViewSet(
    HtmxListMixin, HtmxRetrieveMixin, viewsets.GenericViewSet,
):
    """
    A view set for workers.

    It currently only provides `list` and `retrieve`
    actions (creation is done implicitly when a worker
    comes online; there is no deletion).
    """

    lookup_url_kwarg = "worker"
    serializer_class = WorkerSerializer

    def get_queryset(self):
        """
        Get the queryset for the current action.

        If the user is a member of the account, returns all worker
        for the account (via queues and zones).
        Otherwise, raises permission denied.
        """
        account = get_account(self.kwargs["account"], self.request.user)
        queryset = Worker.objects.filter(queues__zone__account=account).distinct()

        active = self.request.GET.get("active", None)
        if active == "true":
            queryset = queryset.filter(finished__isnull=True)
        elif active == "false":
            queryset = queryset.filter(finished__isnull=False)

        return queryset

    def get_object(self):
        """
        Get the object for the current action.

        Ensures that the users is an account member.
        """
        queryset = self.get_queryset()
        return queryset.get(id=self.kwargs["worker"])


class AccountsWorkersHeartbeatsViewSet(HtmxListMixin, viewsets.GenericViewSet):
    """
    A view set for worker heartbeats.

    Currently only provides a `list` action.
    """

    serializer_class = WorkerHeartbeatSerializer

    def get_queryset(self):
        """
        Get the queryset for the current action.

        If the user is a member of the account, returns all heartbeats
        for the worker.
        Otherwise, raises permission denied.
        """
        get_account(self.kwargs["account"], self.request.user)
        return WorkerHeartbeat.objects.filter(worker=self.kwargs["worker"]).order_by(
            "-time"
        )


class JobsViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    A view set intended for the `overseer` service to update the status of workers.

    Requires that the user is a Stencila staff member.
    Does not require the `overseer` to know which project a job is associated
    with, or have project permission.
    """

    queryset = Job.objects.all()
    serializer_class = JobUpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def partial_update(self, request: Request, pk: int):
        """
        Update a job.

        This action is intended only to be used by the `overseer` service
        for it to update the details of a job based on events
        from the job queue.
        """
        job = self.get_object()
        job.update(data=request.data)
        return Response()


class WorkersViewSet(viewsets.GenericViewSet):
    """
    A view set intended for the `overseer` service to update the status of workers.

    Requires that the user is a Stencila staff member.
    Does not require the `overseer` to know which account a worker is associated
    with, or have account permission.
    """

    permission_classes = [permissions.IsAdminUser]
    lookup_url_kwarg = "hostname"

    # This serializer class is unused here but is necessary to
    # avoid a warning when generating the API schema
    serializer_class = WorkerSerializer

    @swagger_auto_schema(responses={200: "OK"})
    @action(detail=False, methods=["POST"])
    def online(self, request: Request) -> Response:
        """
        Record that a worker has come online.

        An internal route, intended primarily for the `overseer` service.
        Receives event data. Returns an empty response.
        """
        event = request.data

        worker = Worker.get_or_create(event, create=True)
        worker.started = timezone.now()
        worker.save()

        return Response()

    def partial_update(self, request: Request, hostname: str) -> Response:
        """
        Update information on the worker.

        An internal route, intended primarily for the `overseer` service
        and intended to be used once per worker put separately to `/online`.
        Receives data such as which virtual host and queues it is listening
        to. Returns an empty response.
        """
        try:
            worker = Worker.objects.filter(
                hostname=hostname, finished__isnull=True
            ).order_by("-created")[0]
        except IndexError:
            worker = Worker.objects.create(hostname=hostname)

        data = request.data

        stats = data.get("stats", {})
        account_name = stats["broker"]["virtual_host"]
        worker.stats = stats

        queues = data.get("queues", [])
        if queues:
            for queue in queues:
                queue, created = Queue.get_or_create(
                    account_name=account_name, queue_name=queue.get("name", ""),
                )
                worker.queues.add(queue)
        else:
            logger.warning(
                "Worker does not appear to not be listening to any queues",
                extra=dict(worker=worker.signature),
            )

        worker.updated = timezone.now()
        worker.save()

        return Response()

    @swagger_auto_schema(responses={200: "OK"})
    @action(detail=False, methods=["POST"])
    def heartbeat(self, request: Request) -> Response:
        """
        Create a worker heartbeat.

        An internal route, intended primarily for the `overseer` service.
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

    @swagger_auto_schema(responses={200: "OK"})
    @action(detail=False, methods=["POST"])
    def offline(self, request: Request) -> Response:
        """
        Record that a worker has gone offline.

        An internal route, intended primarily for the `overseer` service.
        Receives event data.
        Returns an empty response.
        """
        event = request.data

        worker = Worker.get_or_create(event)
        worker.finished = timezone.now()
        worker.save()

        return Response()


class ProjectsJobsGetAnonThrottle(throttling.AnonRateThrottle):
    """
    Throttle for anonymous users for getting a job.

    This rate is higher than the default to allow for polling of jobs status.
    """

    rate = "3600/hour"  # Allows for one request per second


class ProjectsJobsGetUserThrottle(throttling.UserRateThrottle):
    """
    Throttle for authenticated users for getting a job.
    """

    rate = "10000/hour"


class ProjectsJobsViewSet(
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for jobs.

    Provides basic account CRU(D) views for jobs.
    """

    lookup_url_kwarg = "job"
    object_name = "job"
    queryset_name = "jobs"

    # Actions which allow use of a job key for users that
    # do not have a sufficient role on the project
    actions_key_allowed = ["retrieve", "connect", "cancel"]

    def get_permissions(self):
        """
        Get the permissions that the current action requires.
        """
        if self.action in self.actions_key_allowed:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_throttles(self):
        """
        Get the throttles to apply to the current request.
        """
        if self.action == "get":
            return [
                ProjectsJobsGetAnonThrottle()
                if self.request.user.is_anonymous
                else ProjectsJobsGetUserThrottle()
            ]
        return super().get_throttles()

    def get_project(self) -> Project:
        """
        Get the project, checking that the user necessary role.
        """
        return get_project(
            self.kwargs,
            self.request.user,
            [
                ProjectRole.AUTHOR,
                ProjectRole.EDITOR,
                ProjectRole.MANAGER,
                ProjectRole.OWNER,
            ],
        )

    def get_queryset(self, project: Optional[Project] = None):
        """
        Get the queryset for the current action.

        If the user is a member of the project, or it is a public project,
        returns all jobs for the project.
        Otherwise, raises permission denied.
        """
        project = project or self.get_project()
        return (
            Job.objects.filter(project=project)
            .order_by("-created")
            .select_related(
                "project", "project__account", "creator", "creator__personal_account"
            )
        )

    def get_object(self, project: Optional[Project] = None):
        """
        Get the object for the current action.

        If the user does not have sufficient role on the project
        to access the job, then check for a key for those actions
        where a key is allowed.
        """
        if not project:
            try:
                project = self.get_project()
            except exceptions.NotFound:
                project = None

        job_id = self.kwargs["job"]
        if not project:
            if self.action in self.actions_key_allowed:
                project_id = self.kwargs["project"]
                job_key = self.request.GET.get("key")
                try:
                    return Job.objects.get(project=project_id, id=job_id, key=job_key)
                except Job.DoesNotExist:
                    raise exceptions.NotFound
            else:
                raise exceptions.NotFound
        else:
            queryset = self.get_queryset(project)
            try:
                return queryset.get(id=job_id)
            except Job.DoesNotExist:
                raise exceptions.NotFound

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        For `create`, ensures that the user is a
        project author, manager, or owner.
        """
        if self.action == "list":
            return JobListSerializer
        elif self.action in ("create", "execute"):
            # Get project as permission check
            # Skip when doing API Schema generation
            # (permission check should probably go elsewhere)
            if not getattr(self, "swagger_fake_view", False):
                self.get_project()
            return JobCreateSerializer
        else:
            return JobRetrieveSerializer

    def get_response_context(self, *args, **kwargs):
        """
        Get the template context for HTML responses.
        """
        return super().get_response_context(
            *args,
            **kwargs,
            prev=self.request.GET.get("prev"),
            next=self.request.GET.get("next"),
        )

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
    def connect(self, request, *args, **kwargs) -> Response:
        """
        Connect to a job.

        Redirects to the internal URL so that users can
        connect to the job and run methods inside of it.

        This request it proxied through the `router`. This view
        first checks that the user has permission to edit the job.
        """
        job = self.get_object()

        if not job.urls:
            return Response(
                {"message": "Job is not ready"}, status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if job.ended:
            return Response(
                {"message": "Job has ended"}, status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Record the user that is connecting to the job
        job.add_user(request)

        # Get the correct internal URL based on the request's protocol
        protocol = request.scheme
        if protocol in ("ws", "wss"):
            url = job.urls.get("ws")
        elif protocol in ("http", "https"):
            url = job.urls.get("http")
        else:
            raise RuntimeError(f"Unhandled request scheme {protocol}")

        if url is None:
            return Response(
                {"message": f"Job does not support transport protocol {protocol}"},
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # If necessary, replace `ws` with `http` and let the upgrade to Websocket
        # occur elsewhere. Without this Nginx will respond with the error:
        #  invalid URL prefix in "ws://192.168.1.116:39591/" while reading response header from upstream
        url = re.sub(r"^ws", "http", url)
        path = self.kwargs.get("path")
        url = os.path.join(url, path or "")

        return Response(
            headers={"X-Accel-Redirect": "@jobs-connect", "X-Accel-Redirect-URL": url}
        )

    @swagger_auto_schema(request_body=None)
    @action(detail=True, methods=["PATCH"])
    def cancel(self, request: Request, *args, **kwargs) -> Response:
        """
        Cancel a job.

        If the job is cancellable, it will be cancelled
        and it's status set to `REVOKED`.
        """
        job = self.get_object()
        job.cancel()

        serializer = self.get_serializer(job)
        return Response(serializer.data)
