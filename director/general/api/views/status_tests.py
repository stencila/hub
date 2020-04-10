from unittest import mock

from django.db import OperationalError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import pytest

from version import __version__


class StatusAPIViewTests(APITestCase):
    """Test that unauthenticated user can get status."""

    url = reverse("api-status")
    
    def test_ok(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["time"] is not None
        assert response.data["version"] == __version__

    def test_pending(self):
        with mock.patch(
            "general.api.views.status.migrations_pending", new=migrations_pending_true,
        ):
            response = self.client.get(self.url)
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_db_error(self):
        with mock.patch(
            "general.api.views.status.migrations_pending", new=migrations_pending_operational_error,
        ):
            response = self.client.get(self.url)
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_other_error(self):
        with mock.patch(
            "general.api.views.status.migrations_pending", new=migrations_pending_other_error,
        ):
            with pytest.raises(RuntimeError, match='beep boop'):
                response = self.client.get(self.url)


def migrations_pending_true():
    return True


def migrations_pending_operational_error():
    raise OperationalError("could not connect to server")


def migrations_pending_other_error():
    raise RuntimeError("beep boop")
