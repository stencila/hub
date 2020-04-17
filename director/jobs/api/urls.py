from django.urls import path, include

from general.api.routers import OptionalSlashRouter
from jobs.api.views import AccountJobsViewSet

account_jobs = OptionalSlashRouter()
account_jobs.register("jobs", AccountJobsViewSet, "api-jobs")

urlpatterns = [
    path("accounts/<int:pk>/", include(account_jobs.urls))
]
