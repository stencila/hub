from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action


class AccountJobsViewSet(viewsets.GenericViewSet):
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
        url_path="broker",
        permission_classes=[permissions.IsAdminUser],
        pagination_class=None,
    )
    def broker(self, request, pk: int):
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
