from django.urls import path

import jobs.ui.views as views

urlpatterns = [
    path("", views.JobsListView.as_view(), name="jobs_list"),
    path("<int:job>/details/", views.JobsDetailsView.as_view(), name="jobs_details"),
]
