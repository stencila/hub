from django.shortcuts import redirect, reverse
from rest_framework.response import Response

from jobs.api.serializers import Job, JobRetrieveSerializer
from manager.api.helpers import HtmxMixin


def redirect_to_job(job: Job, accepts_html=False) -> Response:
    """
    Redirect to the URL for the job.
    """
    if accepts_html:
        serializer = JobRetrieveSerializer(job)
        return Response(
            dict(job=job, data=serializer.data),
            status=HtmxMixin.CREATED,
            headers=dict(
                Location=reverse(
                    "ui-projects-jobs-retrieve",
                    args=[job.project.account.name, job.project.name, job.id],
                )
                + "?redirect"
            ),
        )
    else:
        return redirect(
            reverse(
                "api-projects-jobs-detail",
                kwargs=dict(project=job.project.id, job=job.id),
            )
            + "?key="
            + job.key
        )
