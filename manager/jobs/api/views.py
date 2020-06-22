import logging
import os
from typing import List, Optional

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions, mixins, permissions, status, views, viewsets
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
    HtmxMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    filter_from_ident,
)
from projects.api.views.projects import get_project
from projects.models.projects import ProjectRole

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
    HtmxMixin,
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
            self.get_queryset([AccountRole.MANAGER, AccountRole.OWNER])
            return ZoneCreateSerializer
        else:
            return ZoneSerializer


class AccountsQueuesViewSet(
    HtmxMixin, HtmxListMixin, HtmxRetrieveMixin, viewsets.GenericViewSet,
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
    HtmxMixin, HtmxListMixin, HtmxRetrieveMixin, viewsets.GenericViewSet,
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


class AccountsWorkersHeartbeatsViewSet(
    HtmxMixin, HtmxListMixin, viewsets.GenericViewSet
):
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
        job.update()

        serializer = self.get_serializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()


class WorkersViewSet(viewsets.GenericViewSet):
    """
    A view set intended for the `overseer` service to update the status of workers.

    Requires that the user is a Stencila staff member.
    Does not require the `overseer` to know which account a worker is associated
    with, or have account permission.
    """

    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(responses={200: "OK"})
    @action(detail=False, methods=["POST"])
    def online(self, request: Request) -> Response:
        """
        Record that a worker has come online.

        An internal route, intended primarily for the `overseer` service.
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


class ProjectsJobsViewSet(
    HtmxMixin,
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

    def get_queryset(self, roles: Optional[List[ProjectRole]] = None):
        """
        Get the queryset for the current action.

        If the user is a member of the project, or it is a public project,
        returns all jobs for the project.
        Otherwise, raises permission denied.
        """
        project = get_project(self.kwargs["project"], self.request.user, roles)
        return Job.objects.filter(project=project)

    def get_object(self):
        """
        Get the object for the current action.

        Will update details of the job, regardless of the option.
        """
        queryset = self.get_queryset()
        try:
            job = queryset.get(id=self.kwargs["job"])
        except Job.DoesNotExist:
            raise exceptions.NotFound
        job.update()
        return job

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        For `create`, ensures that the user is a
        project author, manager, or owner.
        """
        if self.action in ("create", "execute"):
            self.get_queryset(
                [
                    ProjectRole.AUTHOR,
                    ProjectRole.EDITOR,
                    ProjectRole.MANAGER,
                    ProjectRole.OWNER,
                ]
            )
            return JobCreateSerializer
        elif self.action == "list":
            return JobListSerializer
        else:
            return JobRetrieveSerializer

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
    def cancel(self, request: Request, project: int, job: int) -> Response:
        """
        Cancel a job.

        If the job is cancellable, it will be cancelled
        and it's status set to `REVOKED`.
        """
        # TODO: Check that user has edit rights for job
        job = self.get_object()
        job.cancel()

        serializer = self.get_serializer(job)
        return Response(serializer.data)
