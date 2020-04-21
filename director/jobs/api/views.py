from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from jobs.models import Job
from jobs.api.serializers import (
    JobListSerializer,
    JobCreateSerializer,
    JobRetrieveSerializer,
    JobUpdateSerializer,
)
from jobs.jobs import cancel


class JobsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    # Configuration

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
        return {
            "list": JobListSerializer,
            "create": JobCreateSerializer,
            "retrieve": JobRetrieveSerializer,
            "update": JobUpdateSerializer,
            "partial_update": JobUpdateSerializer,
            "cancel": JobRetrieveSerializer,
        }.get(self.action, JobRetrieveSerializer)

    def perform_create(self, serializer: JobListSerializer):
        """
        Override of `CreateModelMixin.perform_create`.

        Adds the user as the `creator`.
        """
        serializer.validated_data["creator"] = self.request.user
        serializer.save()

    # Proxy views for custom documentation

    # Shortcut views for including the method and params in the URL

    @swagger_auto_schema(request_body=None)
    @action(detail=False, pagination_class=None, methods=["POST"])
    def execute(self, request) -> Response:
        serializer = JobCreateSerializer(
            data={"method": "execute", "params": request.query_params}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Patching views

    @swagger_auto_schema(request_body=None)
    @action(detail=True, methods=["PATCH"])
    def cancel(self, request, pk: int) -> Response:
        """
        Cancel a job.

        If the job is cancellable, it will be cancelled
        and it's status set to `REVOKED`.
        """
        job = cancel(self.get_object())
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
        return Response(headers={"X-Accel-Redirect": "/internal/broker"})
