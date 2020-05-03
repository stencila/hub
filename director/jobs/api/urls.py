from django.urls import path, include

from general.api.routers import OptionalSlashRouter
from jobs.api.views import (
    JobsViewSet,
    AccountsJobsViewSet,
    AccountsZonesViewSet,
    WorkersViewSet,
    WorkersStatusesViewSet,
)

jobs = OptionalSlashRouter()
jobs.register("jobs", JobsViewSet, "api-jobs")

accounts_jobs = OptionalSlashRouter()
accounts_jobs.register("jobs", AccountsJobsViewSet, "api-accounts-jobs")

accounts_zones = OptionalSlashRouter()
accounts_zones.register("zones", AccountsZonesViewSet, "api-accounts-zones")

workers = OptionalSlashRouter()
workers.register("workers", WorkersViewSet, "api-workers")

workers_statuses = OptionalSlashRouter()
workers_statuses.register("statuses", WorkersStatusesViewSet, "api-workers-statuses")

urlpatterns = (
    jobs.urls
    + [
        path("accounts/<int:pk>/", include(accounts_jobs.urls)),
        path("accounts/<int:pk>/", include(accounts_zones.urls)),
    ]
    + workers.urls
    + [path("workers/<int:pk>/", include(workers_statuses.urls))]
)
