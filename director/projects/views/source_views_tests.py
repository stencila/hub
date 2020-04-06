from unittest import mock

from django.test import TestCase

from projects.views.source_views import SourceCreateView


class SourceCreateViewTestCase(TestCase):
    def test_path_setting_from_url(self):
        """Test the initial `path` value is populated from the request URL."""
        view = SourceCreateView()
        view.kwargs = {"account_name": "account-name", "project_name": "project-name"}

        request = mock.MagicMock(name="request")
        view.get_project = mock.MagicMock(name="get_project")
        request.GET = {"path": "path/to/thing"}

        view.request = request

        initial = view.get_initial()
        self.assertEqual(
            initial, {"project": view.get_project.return_value, "path": "path/to/thing"}
        )

    def test_default_path(self):
        """If no path is provided in GET, it should default to '.'."""
        view = SourceCreateView()
        view.kwargs = {"account_name": "account-name", "project_name": "project-name"}

        request = mock.MagicMock(name="request")
        view.get_project = mock.MagicMock(name="get_project")
        request.GET = {}

        view.request = request

        initial = view.get_initial()
        self.assertEqual(
            initial, {"project": view.get_project.return_value, "path": "."}
        )
