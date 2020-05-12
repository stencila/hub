from django.urls import path

import jobs.ui.views as views

urlpatterns = [path("", views.JobsListView.as_view(), name="jobs_list")]
