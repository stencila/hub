from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.test import TestCase
from django.utils import timezone

from projects.cloud_session_controller import CloudSessionFacade, ActiveSessionsExceededException
from projects.permission_facade import ProjectFetchResult
from projects.project_host_views import ProjectHostSessionsView, ProjectSessionRequestView
from projects.project_models import Project
from projects.session_models import Session, SessionRequest

ob_get_path = 'projects.project_host_views.get_object_or_404'


class ProjectHostSessionsViewTests(TestCase):
    def setUp(self):
        self.view = ProjectHostSessionsView()
        self.view.session_facade = mock.MagicMock(spec=CloudSessionFacade, name='CloudSessionFacade')
        self.request = mock.MagicMock(spec=HttpRequest, name='request')
        self.request.user = mock.MagicMock(spec=User)
        self.token = 'token'
        self.environ = 'environ'

    def test_project_access_denied(self):
        """If a `Project` has a key but it does not match the one provided in the POST data, raise `PermissionDenied`"""
        with mock.patch(ob_get_path, return_value=mock.MagicMock(spec=Project)) as mock_fetch:
            mock_fetch.return_value.key = 'project_key'

            self.request.POST = {'key': 'invalid'}

            with self.assertRaises(PermissionDenied):
                self.view.post(self.request, self.token, self.environ)

    def test_get_session_url_from_request_session_not_set(self):
        """
        If a URL is not in the session (key in the format CLOUD_SESSION_URL_$token_$environ) then URL should be `None`.
        """
        self.request.session = dict()

        url = self.view.get_session_from_request_session(self.request, 'CLOUD_SESSION_URL_token_environ')
        self.assertIsNone(url)

    @mock.patch('projects.project_host_views.Session', spec=Session)
    def test_get_session_url_from_request_session_no_session_object(self, mock_session_class):
        """If `Session.DoesNotExist` is raised when getting the `Session` by URL, then `None` should be returned"""
        mock_session_class.objects = mock.MagicMock(name='Session.objects')
        mock_session_class.DoesNotExist = Session.DoesNotExist
        mock_session_class.objects.get.side_effect = Session.DoesNotExist

        self.request.session = {'CLOUD_SESSION_URL_token_environ': 'http://session.url'}

        url = self.view.get_session_from_request_session(self.request, 'CLOUD_SESSION_URL_token_environ')

        self.assertIsNone(url)
        mock_session_class.objects.get.assert_called_with(url='http://session.url')

    @mock.patch('projects.project_host_views.Session', spec=Session)
    def test_get_session_url_from_request_session_stopped_session(self, mock_session_class):
        """If the `Session` was found by URL, but is stopped, then `None` should be returned."""
        mock_session_class.objects = mock.MagicMock(name='Session.objects')
        mock_session = mock.MagicMock(spec=Session, name='Session')
        mock_session.stopped = timezone.now() - timedelta(seconds=300)  # just needs to be any time in the past

        mock_session_class.objects.get.return_value = mock_session

        self.request.session = {'CLOUD_SESSION_URL_token_environ': 'http://session.url'}

        url = self.view.get_session_from_request_session(self.request, 'CLOUD_SESSION_URL_token_environ')

        self.assertIsNone(url)
        mock_session_class.objects.get.assert_called_with(url='http://session.url')

    @mock.patch('projects.project_host_views.Session', spec=Session)
    def test_get_session_url_from_request_session_success(self, mock_session_class):
        """If the `Session` was found by URL, and is not stopped then we should get the URL back."""
        mock_session_class.objects = mock.MagicMock(name='Session.objects')
        mock_session = mock.MagicMock(spec=Session, name='Session')
        mock_session.stopped = None

        mock_session_class.objects.get.return_value = mock_session

        self.request.session = {'CLOUD_SESSION_URL_token_environ': 'http://session.url'}

        session = self.view.get_session_from_request_session(self.request, 'CLOUD_SESSION_URL_token_environ')

        self.view.session_facade.update_session_info.assert_called_with(mock_session)
        mock_session_class.objects.get.assert_called_with(url='http://session.url')

        self.assertEqual(session, mock_session)

    def test_get_session_request_to_use_no_session_request(self):
        """
        If there is no pk for the `SessionRequest` to use in the `request` session, then the `SessionRequest` to use
        should be `None`
        """
        self.request.session = {}

        session_request = self.view.get_session_request_to_use(self.request, self.token)

        self.assertIsNone(session_request)

    @mock.patch('projects.project_host_views.SessionRequest', spec=SessionRequest)
    def test_get_session_request_to_use(self, mock_session_request_class):
        """
        If the `SessionRequest` pk is set in the SESSION_REQUEST_ID_$token session variable, load the `SessionRequest`
        with that pk.
        """
        mock_session_request_class.objects = mock.MagicMock(name='SessionRequest.objects')

        self.request.session = {'SESSION_REQUEST_NEXT_token': True,
                                'SESSION_REQUEST_ID_token': 5}

        session_request = self.view.get_session_request_to_use(self.request, self.token)

        mock_session_request_class.objects.get.assert_called_with(pk=5)

        self.assertNotIn('SESSION_REQUEST_NEXT_token', self.request.session)
        self.assertNotIn('SESSION_REQUEST_ID_5', self.request.session)

        self.assertEqual(session_request, mock_session_request_class.objects.get.return_value)

    @mock.patch('projects.project_host_views.reverse')
    @mock.patch('projects.project_host_views.redirect')
    def test_create_session_request(self, mock_redirect, mock_reverse):
        """
        `create_session_request` should get a `SessionRequest` back from the `create_session_request` method of the
        `CloudSessionFacade`, and set its pk into the session, then return a redirect to the view for checking
        the status of this
        """
        self.request.session = {}

        response = self.view.create_session_request(self.request, self.token, self.environ)

        self.view.session_facade.create_session_request.assert_called_with(self.environ)
        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_with(mock_reverse.return_value)
        mock_reverse.assert_called_with('session_queue_v0', args=(self.token,))

        self.assertEqual(self.request.session["SESSION_REQUEST_ID_token"],
                         self.view.session_facade.create_session_request.return_value.pk)

    def test_create_session(self):
        """
        `create_session` should attempt to create a `Session` using the optional `session_request_to_use`, then setting
        the returned `Session`'s url into the request session and returning it
        """
        self.request.session = {}

        session_key = 'CLOUD_SESSION_URL_token_environ'
        session_request_to_use = mock.MagicMock(spec=SessionRequest, name="session_request_to_use")
        session = self.view.create_session(self.request, self.environ, session_key, session_request_to_use)

        self.assertEqual(session.url, self.view.session_facade.create_session.return_value.url)
        self.assertEqual(self.request.session[session_key], session.url)

    @mock.patch('projects.project_host_views.JsonResponse')
    def test_generate_response_existing_session_url(self, mock_json_response_class):
        """
        When passing in a `session to `generate_response`, a new `Session`/URL should not be generated, instead the
        response should be returned with this URL.
        """
        mock_session = mock.MagicMock(spec=Session, name='session')
        session_url = "http://session.url"
        mock_session.url = session_url
        extra_auth_parameters = mock.MagicMock(spec=dict)

        self.view.get_session_request_to_use = mock.MagicMock(name='get_session_request_to_use')
        self.view.create_session = mock.MagicMock(name='create_session')

        response = self.view.generate_response(self.request, self.environ, 'session_key', self.token, mock_session,
                                               extra_auth_parameters)

        self.assertEqual(response, mock_json_response_class.return_value)

        self.view.get_session_request_to_use.assert_not_called()
        self.view.create_session.assert_not_called()
        self.view.session_facade.generate_external_location.assert_called_with(mock_session, extra_auth_parameters)

        mock_json_response_class.assert_called_with({
            'location': self.view.session_facade.generate_external_location.return_value.to_dict.return_value
        })

    @mock.patch('projects.project_host_views.JsonResponse')
    def test_generate_response_create_session_success(self, mock_json_response_class):
        """
        If no `session` is passed to `generate_response` a new `Session` should attempt to be generated by calling
        `create_session`
        """
        self.view.get_session_request_to_use = mock.MagicMock(name='get_session_request_to_use')
        self.view.create_session = mock.MagicMock(name='create_session')
        self.view.create_session_request = mock.MagicMock(name='self.create_session_request')
        extra_auth_parameters = mock.MagicMock(spec=dict)

        response = self.view.generate_response(self.request, self.environ, 'session_key', self.token, None,
                                               extra_auth_parameters)

        self.assertEqual(response, mock_json_response_class.return_value)

        self.view.create_session.assert_called_with(self.request, self.environ, 'session_key',
                                                    self.view.get_session_request_to_use.return_value)

        self.view.session_facade.generate_external_location.assert_called_with(
            self.view.create_session.return_value, extra_auth_parameters)
        mock_json_response_class.assert_called_with({
            'location': self.view.session_facade.generate_external_location.return_value.to_dict.return_value
        })
        self.view.create_session_request.assert_not_called()

    def test_generate_response_create_session_exception(self):
        """
        If no `session_url` is passed to `generate_response` a new `Session` should attempt to be generated by calling
        `create_session` - if that fails with an `ActiveSessionsExceededException`, `create_session_request` is called.
        """
        self.view.get_session_request_to_use = mock.MagicMock(name='get_session_request_to_use')
        self.view.create_session = mock.MagicMock(name='create_session', side_effect=ActiveSessionsExceededException)
        self.view.create_session_request = mock.MagicMock(name='self.create_session_request')

        response = self.view.generate_response(self.request, self.environ, 'session_key', self.token, None)

        self.assertEqual(response, self.view.create_session_request.return_value)
        self.view.create_session_request.assert_called_with(self.request, self.token, self.environ)

    @mock.patch(ob_get_path)
    def test_post(self, mock_get_object_or_404):
        """
        Test the general post flow with mocks
        """
        project = mock.MagicMock(spec=Project)
        project.key = None
        project.id = 47
        mock_get_object_or_404.return_value = project

        self.view.setup_cloud_client = mock.MagicMock(name='setup_cloud_client')
        self.view.get_session_from_request_session = mock.MagicMock(name='get_session_from_request_session')
        self.view.generate_response = mock.MagicMock(name='generate_response')
        self.view.project_fetch_result = mock.MagicMock(spec=ProjectFetchResult, name='project_fetch_result')
        self.view.perform_project_fetch = mock.MagicMock(name='perform_project_fetch')
        self.request.GET = {'path': 'main.xml'}

        response = self.view.post(self.request, self.token, self.environ)

        self.view.setup_cloud_client.assert_called_with(project)

        self.view.get_session_from_request_session.assert_called_with(self.request,
                                                                      'CLOUD_SESSION_URL_token_environ')

        self.view.generate_response.assert_called_with(self.request, self.environ, 'CLOUD_SESSION_URL_token_environ',
                                                       self.token,
                                                       self.view.get_session_from_request_session.return_value,
                                                       {'role': None, 'path': '47/main.xml'})

        self.assertEqual(response, self.view.generate_response.return_value)


class TestProjectSessionRequestView(TestCase):
    def setUp(self):
        self.view = ProjectSessionRequestView()
        self.view.session_facade = mock.MagicMock(spec=CloudSessionFacade, name='CloudSessionFacade')
        self.request = mock.MagicMock(spec=HttpRequest, name='request')
        self.token = 'token'
        self.environ = 'environ'

    def test_get_session_request_no_session_key(self):
        """
        `get_session_request` should return `None` if the session request key is not in the request session.
        """
        self.request.session = {}

        session_request = self.view.get_session_request(self.request, self.token)

        self.assertIsNone(session_request)

    @mock.patch('projects.project_host_views.SessionRequest', spec=SessionRequest)
    def test_get_session_request_success(self, session_request_class):
        """
        `get_session_request` should query the DB using the pk stored in the session to load a `SessionRequest`
        """
        self.request.session = {
            'SESSION_REQUEST_ID_token': 100
        }

        session_request_class.objects = mock.MagicMock(name='objects')

        session_request = self.view.get_session_request(self.request, self.token)

        session_request_class.objects.get.assert_called_with(pk=100)
        self.assertEqual(session_request, session_request_class.objects.get.return_value)

    @mock.patch('projects.project_host_views.SessionRequest', spec=SessionRequest)
    def test_get_session_request_not_found(self, session_request_class):
        """
        `get_session_request` should query the DB using the pk stored in the session to load a `SessionRequest`, if it
        is not found removed the ID from the request session and return None.
        """
        self.request.session = {
            'SESSION_REQUEST_ID_token': 100
        }

        session_request_class.objects = mock.MagicMock(name='objects')
        session_request_class.DoesNotExist = SessionRequest.DoesNotExist
        session_request_class.objects.get.side_effect = SessionRequest.DoesNotExist

        session_request = self.view.get_session_request(self.request, self.token)

        session_request_class.objects.get.assert_called_with(pk=100)
        self.assertIsNone(session_request)
        self.assertNotIn('SESSION_REQUEST_ID_token', self.request.session)

    def test_project_has_sessions_available_none_setting(self):
        """If `Project.session_concurrent` is `None`, it should always have sessions available."""
        project = mock.MagicMock(spec=Project, name='Project')
        project.sessions_concurrent = None
        self.assertTrue(self.view.project_has_sessions_available(project))

    def test_project_has_sessions_available(self):
        """
        If `Project.session_concurrent` is not `None`, `project_has_sessions_available` should compare this to the
        number of available `Session`s for the `Project`. If it is fewer, return `False`.
        """
        project = mock.MagicMock(spec=Project, name='Project')

        project.sessions_concurrent = 5
        self.view.session_facade.get_active_session_count.return_value = 10
        self.assertFalse(self.view.project_has_sessions_available(project))

        project.sessions_concurrent = 10
        self.view.session_facade.get_active_session_count.return_value = 10
        self.assertFalse(self.view.project_has_sessions_available(project))

        project.sessions_concurrent = 100
        self.view.session_facade.get_active_session_count.return_value = 99
        self.assertTrue(self.view.project_has_sessions_available(project))

    def test_session_can_start_no_sessions_available(self):
        """
        If there are no `Session`s available (`project_sessions_available` returns `False`) then `session_can_start`
        should also return `False`.
        """
        project = mock.MagicMock(spec=Project, name='Project')
        session_request = mock.MagicMock(spec=SessionRequest, name='SessionRequest')
        self.view.project_has_sessions_available = mock.MagicMock(name='project_has_sessions_available',
                                                                  return_value=False)

        self.assertFalse(self.view.session_can_start(self.request, project, self.token, session_request))

        self.view.project_has_sessions_available.assert_called_with(project)

    def test_session_can_start_request_not_first_in_queue(self):
        """
        If there are `Session`s available, but the supplied `session_request` is not the first in the queue, then
        `session_can_start` should return `False`.
        """
        project = mock.MagicMock(spec=Project, name='Project')
        session_request = mock.MagicMock(spec=SessionRequest, name='SessionRequest')
        self.view.project_has_sessions_available = mock.MagicMock(name='project_has_sessions_available',
                                                                  return_value=True)
        self.view.get_first_session_request = mock.MagicMock(name='get_first_session_request')

        self.assertFalse(self.view.session_can_start(self.request, project, self.token, session_request))

        self.view.project_has_sessions_available.assert_called_with(project)
        self.view.get_first_session_request.assert_called_with(project)

    def test_session_can_start_success(self):
        """
        If there are `Sessions`s available and the `session_request` matches the first in the queue, then
        `session_can_start` should return `True`. A semaphore indicating the session can start is added to the request
        session.
        """
        self.request.session = {}
        project = mock.MagicMock(spec=Project, name='Project')
        session_request = mock.MagicMock(spec=SessionRequest, name='SessionRequest')
        self.view.project_has_sessions_available = mock.MagicMock(name='project_has_sessions_available',
                                                                  return_value=True)
        self.view.get_first_session_request = mock.MagicMock(name='get_first_session_request',
                                                             return_value=session_request)

        self.assertTrue(self.view.session_can_start(self.request, project, self.token, session_request))

        self.view.project_has_sessions_available.assert_called_with(project)
        self.view.get_first_session_request.assert_called_with(project)
        self.assertTrue(self.request.session['SESSION_REQUEST_NEXT_token'])

    @mock.patch('projects.project_host_views.get_object_or_404')
    @mock.patch('projects.project_host_views.JsonResponse')
    def test_get_with_invalid_session_request(self, mock_json_response_class, mock_get_object):
        project = mock.MagicMock(spec=Project, name='Project')
        mock_get_object.return_value = project
        self.view.get_session_request = mock.MagicMock(name='get_session_request')

        self.view.get_session_request.return_value = None

        response = self.view.get(self.request, self.token)

        self.view.get_session_request.assert_called_with(self.request, self.token)
        self.assertEqual(response, mock_json_response_class.return_value)
        mock_json_response_class.assert_called_with(
            {'invalid_session': True}
        )

    @mock.patch('projects.project_host_views.get_object_or_404')
    @mock.patch('projects.project_host_views.JsonResponse')
    @mock.patch('projects.project_host_views.settings')
    def test_get_with_success(self, mock_settings, mock_json_response_class, mock_get_object):
        mock_settings.EXECUTION_SERVER_HOST = 'server_host'
        mock_settings.EXECUTION_SERVER_PROXY_PATH = '/proxy'
        mock_settings.JWT_SECRET = 'abc123'

        project = mock.MagicMock(spec=Project, name='Project')
        mock_get_object.return_value = project
        self.view.get_session_request = mock.MagicMock(name='get_session_request')
        self.view.session_can_start = mock.MagicMock(name='session_can_start')

        response = self.view.get(self.request, self.token)

        self.view.get_session_request.assert_called_with(self.request, self.token)
        self.assertEqual(response, mock_json_response_class.return_value)
        mock_json_response_class.assert_called_with(
            {'start_session': self.view.session_can_start.return_value}
        )

        self.view.session_can_start.assert_called_with(self.request, project, self.token,
                                                       self.view.get_session_request.return_value)
