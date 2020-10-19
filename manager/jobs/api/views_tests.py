from rest_framework import status

from manager.testing import DatabaseTestCase


class ProjectsJobsViewsTest(DatabaseTestCase):
    """Test creating and retrieving jobs for a project."""

    # Type specific CRUD methods for Jobs

    def create_job(self, user, project, data):
        return self.create(
            user, "api-projects-jobs-list", data, kwargs={"project": project.id}
        )

    def retrieve_job(self, user, project, job_id, job_key=None):
        return self.retrieve(
            user,
            "api-projects-jobs-detail",
            kwargs={"project": project.id, "job": job_id},
            data=dict(key=job_key) if job_key else {},
        )

    # Testing methods

    def test_access_with_and_without_keys(self):
        """
        Tests access to a job, with and without a key, for a public project.
        """
        for project in (self.ada_public, self.ada_private):
            response = self.create_job(self.ada, project, dict(method="sleep"))
            assert response.status_code == status.HTTP_201_CREATED
            job_id = response.data.get("id")
            job_key = response.data.get("key")

            # Ada can get the job details with or without key and
            # even with a bad key
            response = self.retrieve_job(self.ada, project, job_id)
            assert response.status_code == status.HTTP_200_OK
            response = self.retrieve_job(self.ada, project, job_id, job_key)
            assert response.status_code == status.HTTP_200_OK
            response = self.retrieve_job(self.ada, project, job_id, "foo")
            assert response.status_code == status.HTTP_200_OK

            # Bob and anon...
            for user in (self.bob, None):
                #  can't get job without key
                response = self.retrieve_job(user, project, job_id)
                assert response.status_code == status.HTTP_404_NOT_FOUND

                # can get job with key
                response = self.retrieve_job(user, project, job_id, job_key)
                assert response.status_code == status.HTTP_200_OK

                # can't get job with bad key
                response = self.retrieve_job(user, project, job_id, "foo")
                assert response.status_code == status.HTTP_404_NOT_FOUND
