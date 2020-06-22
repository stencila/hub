from django.urls import include, path

from jobs.api.views import (
    AccountsBrokerView,
    AccountsQueuesViewSet,
    AccountsWorkersHeartbeatsViewSet,
    AccountsWorkersViewSet,
    AccountsZonesViewSet,
    JobsViewSet,
    ProjectsJobsViewSet,
    WorkersViewSet,
)
from manager.api.routers import OptionalSlashRouter

# Public routes, nested under accounts or projects

projects_jobs = OptionalSlashRouter()
projects_jobs.register("jobs", ProjectsJobsViewSet, "api-projects-jobs")

accounts_zones = OptionalSlashRouter()
accounts_zones.register("zones", AccountsZonesViewSet, "api-accounts-zones")

accounts_queues = OptionalSlashRouter()
accounts_queues.register("queues", AccountsQueuesViewSet, "api-accounts-queues")

accounts_workers = OptionalSlashRouter()
accounts_workers.register("workers", AccountsWorkersViewSet, "api-accounts-workers")

accounts_workers_heartbeats = OptionalSlashRouter()
accounts_workers_heartbeats.register(
    "heartbeats", AccountsWorkersHeartbeatsViewSet, "api-accounts-workers-heartbeats"
)

# Routes for overseer, not nested under accounts or projects

jobs = OptionalSlashRouter()
jobs.register("jobs", JobsViewSet, "api-jobs")

workers = OptionalSlashRouter()
workers.register("workers", WorkersViewSet, "api-workers")


urlpatterns = (
    [
        path("accounts/<account>/broker", AccountsBrokerView.as_view()),
        path("accounts/<account>/", include(accounts_zones.urls)),
        path("accounts/<account>/", include(accounts_queues.urls)),
        path("accounts/<account>/", include(accounts_workers.urls)),
        path(
            "accounts/<account>/workers/<worker>/",
            include(accounts_workers_heartbeats.urls),
        ),
        path("projects/<project>/", include(projects_jobs.urls)),
    ]
    + jobs.urls
    + workers.urls
)
