from django.test import TestCase

from unittest import mock

from requests import HTTPError

from projects.cloud_session_controller import CloudClient, CloudSessionFacade, SessionException, \
    ActiveSessionsExceededException
from projects.project_models import Project
from projects.session_models import SessionRequest, SessionStatus


class SessionFacadeTests(TestCase):
    def setUp(self):
        self.project = mock.MagicMock(spec=Project, name="Project")
        self.client = mock.MagicMock(spec=CloudClient, name="CloudClient")
        self.cs_facade = CloudSessionFacade(self.project, self.client)

    def test_init(self):
        """
        Test `project` and `client` are set on ` CloudSessionFacade` __init__
        """
        self.assertEqual(self.project, self.cs_facade.project)
        self.assertEqual(self.client, self.cs_facade.client)

    def test_session_requests_exist_true(self):
        """
        If the count of `session_requests` on the `Project` is > 0 then `session_requests_exist` should return `True`
        """
        self.project.session_requests.count.return_value = 1
        self.assertTrue(self.cs_facade.session_requests_exist())

    def test_session_requests_exist_false(self):
        """
        If the count of `session_requests` on the `Project` = 0 then `session_requests_exist` should return `False`
        """
        self.project.session_requests.count.return_value = 0
        self.assertFalse(self.cs_facade.session_requests_exist())

    def test_check_session_queue_full_none_success(self):
        """
        If the `Project` has `sessions_queued` of `None` then `check_session_queue_full` should always run successfully
        (no Exception raised)
        """
        self.project.sessions_queued = None

        self.project.session_requests.count.return_value = 0
        self.cs_facade.check_session_queue_full()

        self.project.session_requests.count.return_value = 1000
        self.cs_facade.check_session_queue_full()

    def test_check_session_queue_full_zero_failure(self):
        """
        If the `Project` has `sessions_queued` of 0 then `check_session_queue_full` should always fail
        """
        self.project.sessions_queued = 0

        self.project.session_requests.count.return_value = 0
        with self.assertRaises(SessionException):
            self.cs_facade.check_session_queue_full()

        self.project.session_requests.count.return_value = 1000
        with self.assertRaises(SessionException):
            self.cs_facade.check_session_queue_full()

    def test_check_session_queue_full_standard(self):
        """
        If the `Project` has `sessions_queued` of something other than None or 0 then `check_session_queue_full` then it
        should succeed or fail based on the count of its `SessionRequest`s
        """
        self.project.sessions_queued = 1

        self.project.session_requests.count.return_value = 1
        with self.assertRaises(SessionException):
            self.cs_facade.check_session_queue_full()

        self.project.sessions_queued = 1000
        self.project.session_requests.count.return_value = 1001
        with self.assertRaises(SessionException):
            self.cs_facade.check_session_queue_full()

        self.project.sessions_queued = 10
        self.project.session_requests.count.return_value = 9
        self.cs_facade.check_session_queue_full()  # no exception raised

    def test_check_total_sessions_exceeded_none_success(self):
        """
        If the `Project` has `sessions_total` of `None` then `check_total_sessions_exceeded` should always succeed
        (no exception raised)
        """
        self.project.sessions_total = None

        self.project.sessions.count.return_value = 0
        self.cs_facade.check_total_sessions_exceeded()

        self.project.sessions.count.return_value = 100
        self.cs_facade.check_total_sessions_exceeded()

    def test_check_total_sessions_exceeded_zero_failure(self):
        """
        If the `Project` has `sessions_total` of 0 then `check_total_sessions_exceeded` should always fail by raising
        a `SessionException`
        """
        self.project.sessions_total = 0

        self.project.sessions.count.return_value = 0
        with self.assertRaises(SessionException):
            self.cs_facade.check_total_sessions_exceeded()

        self.project.sessions.count.return_value = 100
        with self.assertRaises(SessionException):
            self.cs_facade.check_total_sessions_exceeded()

    def test_check_total_sessions_exceeded_standard(self):
        """
        If the `Project` has `sessions_total` of something other than `None` or 0 it should succeed or fail based on
        the count of its `Session`s
        """
        self.project.sessions_total = 100

        self.project.sessions.count.return_value = 100
        with self.assertRaises(SessionException):
            self.cs_facade.check_total_sessions_exceeded()

        self.project.sessions.count.return_value = 101
        with self.assertRaises(SessionException):
            self.cs_facade.check_total_sessions_exceeded()

        self.project.sessions.count.return_value = 99
        self.cs_facade.check_total_sessions_exceeded()  # no exception raised

    def test_check_active_sessions_exceeded_none_success(self):
        """
        If the `Project` has `sessions_active` of `None` then `check_active_sessions_exceeded` should always succeed
        (no exception raised)
        """
        self.project.sessions_concurrent = None
        self.cs_facade.get_active_session_count = mock.MagicMock(name="get_active_session_count")

        self.cs_facade.get_active_session_count.return_value = 0
        self.cs_facade.check_active_sessions_exceeded()

        self.cs_facade.get_active_session_count.return_value = 100
        self.cs_facade.check_active_sessions_exceeded()

    def test_check_active_sessions_exceeded_zero_failure(self):
        """
        If the `Project` has `sessions_active` of 0 then `check_active_sessions_exceeded` should always fail by raising
        a `SessionException`
        """
        self.project.sessions_concurrent = 0
        self.cs_facade.get_active_session_count = mock.MagicMock(name="get_active_session_count")

        self.cs_facade.get_active_session_count.return_value = 0
        with self.assertRaises(SessionException):
            self.cs_facade.check_active_sessions_exceeded()

        self.cs_facade.get_active_session_count.return_value = 100
        with self.assertRaises(SessionException):
            self.cs_facade.check_active_sessions_exceeded()

    def test_check_active_sessions_exceeded_standard(self):
        """
        If the `Project` has `sessions_active` of something other than `None` or 0 it should succeed or fail based on
        the count of its active `Session`s
        """
        self.project.sessions_concurrent = 100
        self.cs_facade.get_active_session_count = mock.MagicMock(name="get_active_session_count")

        self.cs_facade.get_active_session_count.return_value = 100
        with self.assertRaises(SessionException):
            self.cs_facade.check_active_sessions_exceeded()

        self.cs_facade.get_active_session_count.return_value = 101
        with self.assertRaises(SessionException):
            self.cs_facade.check_active_sessions_exceeded()

        self.cs_facade.get_active_session_count.return_value = 99
        self.cs_facade.check_active_sessions_exceeded()  # no exception raised

    def test_check_session_requests_exist_request_session_passed(self):
        """
        If a `session_request_to_use` is passed in then `check_session_requests_exist` should always return without
        raising an exception
        """
        sr_to_use = mock.MagicMock(spec=SessionRequest)
        self.cs_facade.session_requests_exist = mock.MagicMock(return_value=0)

        self.cs_facade.check_session_requests_exist(sr_to_use)  # no Exception -> Success
        sr_to_use.delete.assert_called_with()  # should be deleted after use

        sr_to_use.reset_mock()
        self.cs_facade.session_requests_exist = mock.MagicMock(return_value=10)
        self.cs_facade.check_session_requests_exist(sr_to_use)  # no Exception -> Success
        sr_to_use.delete.assert_called_with()  # should be deleted after use

    def test_check_session_requests_exist_no_request_session_passed(self):
        """
        If `session_request_to_use` is passed in as `None` then `check_session_requests_exist` should raise
        `ActiveSessionsExceededException` if there are `SessionRequest`s for the project. If not, they should
        """
        self.cs_facade.session_requests_exist = mock.MagicMock(return_value=0)
        self.cs_facade.check_session_requests_exist(None)  # no Exception -> Success

        self.cs_facade.session_requests_exist = mock.MagicMock(return_value=10)

        with self.assertRaises(ActiveSessionsExceededException):
            self.cs_facade.check_session_requests_exist(None)

    def test_create_session_request(self):
        """
        `create_session_request` should expire old `SessionRequest`s, check if a new one can be created, then create one
        """
        self.cs_facade.expire_stale_session_requests = mock.MagicMock(name="expire_stale_session_requests")
        self.cs_facade.check_session_queue_full = mock.MagicMock(name="check_session_queue_full")

        session_request = self.cs_facade.create_session_request("environ_name")

        self.cs_facade.expire_stale_session_requests.assert_called_with()
        self.cs_facade.expire_stale_session_requests.check_session_queue_full()
        self.assertEqual(self.project.session_requests.create.return_value, session_request)
        self.project.session_requests.create.assert_called_with(environ="environ_name")

    def test_check_session_can_start(self):
        """Test that all the check functions are called."""
        self.cs_facade.check_total_sessions_exceeded = mock.MagicMock(name="check_total_sessions_exceeded")
        self.cs_facade.check_active_sessions_exceeded = mock.MagicMock(name="check_active_sessions_exceeded")
        self.cs_facade.check_session_requests_exist = mock.MagicMock(name="check_session_requests_exist")
        session_request_to_use = mock.MagicMock(spec=SessionRequest)

        self.cs_facade.check_session_can_start(session_request_to_use)

        self.cs_facade.check_total_sessions_exceeded.assert_called_with()
        self.cs_facade.check_active_sessions_exceeded.assert_called_with()
        self.cs_facade.check_session_requests_exist.assert_called_with(session_request_to_use)

    def test_perform_session_create(self):
        """Test that the session is started with a client `start_session` call, and a new `Session` is returned. """
        environ = "environ"
        session_parameters = mock.MagicMock(spec=dict)

        with mock.patch("projects.cloud_session_controller.Session") as mock_session_class:
            with mock.patch("projects.cloud_session_controller.timezone") as mock_timezone:
                session = self.cs_facade.perform_session_create(environ, session_parameters)

        self.client.start_session.assert_called_with(environ, session_parameters)
        self.assertEqual(mock_session_class.objects.create.return_value, session)
        mock_session_class.objects.create.assert_called_with(
            project=self.project,
            started=mock_timezone.now.return_value,
            last_check=mock_timezone.now.return_value,
            url=self.client.start_session.return_value.url,
            execution_id=self.client.start_session.return_value.execution_id
        )

    @mock.patch('projects.cloud_session_controller.timezone')
    def test_update_session_info_with_404(self, mock_timezone):
        """
        If the query to get Session information from the Cloud returns 404, an HttpError is raised, and we should assume
        that the Session has stopped.
        """
        mock_response = mock.MagicMock()
        mock_response.status_code = 404
        self.client.get_session_info.side_effect = HTTPError(response=mock_response)
        mock_session = mock.MagicMock()

        self.cs_facade.update_session_info(mock_session)

        self.assertEqual(mock_session.stopped, mock_timezone.now.return_value)

    def test_update_session_with_other_http_error(self):
        """
        If the query to get Session information from the Cloud raises an HttpError that does not have a 404 status, then
        that exception should be raised.
        """
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        self.client.get_session_info.side_effect = HTTPError(response=mock_response)
        mock_session = mock.MagicMock()

        with self.assertRaises(HTTPError):
            self.cs_facade.update_session_info(mock_session)

    @staticmethod
    def get_session_for_update():
        mock_session = mock.MagicMock()
        mock_session.last_check = None
        mock_session.started = None
        mock_session.stopped = None
        return mock_session

    def test_update_session_with_unknown(self):
        """If client.get_session_info returns SessionStatus.UNKNOWN, no changes should be made to the Session."""
        session_info = mock.MagicMock()
        session_info.status = SessionStatus.UNKNOWN
        self.client.get_session_info.return_value = session_info
        mock_session = self.get_session_for_update()

        self.cs_facade.update_session_info(mock_session)

        self.client.get_session_info.assert_called_with(mock_session)
        self.assertIsNone(mock_session.last_check)
        self.assertIsNone(mock_session.started)
        self.assertIsNone(mock_session.stopped)

    @mock.patch('projects.cloud_session_controller.timezone')
    def test_update_session_with_running(self, mock_timezone):
        """
        If client.get_session_info returns SessionStatus.RUNNING, session.started should be set to the current time.
        """
        session_info = mock.MagicMock()
        session_info.status = SessionStatus.RUNNING
        self.client.get_session_info.return_value = session_info
        mock_session = self.get_session_for_update()

        self.cs_facade.update_session_info(mock_session)

        self.client.get_session_info.assert_called_with(mock_session)
        self.assertEqual(mock_session.last_check, mock_timezone.now.return_value)
        self.assertEqual(mock_session.started, mock_timezone.now.return_value)
        self.assertIsNone(mock_session.stopped)

    @mock.patch('projects.cloud_session_controller.timezone')
    def test_update_session_with_stopped(self, mock_timezone):
        """
        If client.get_session_info returns SessionStatus.STOPPED, session.stopped should be set to the current time.
        """
        session_info = mock.MagicMock()
        session_info.status = SessionStatus.STOPPED
        self.client.get_session_info.return_value = session_info
        mock_session = self.get_session_for_update()

        self.cs_facade.update_session_info(mock_session)

        self.client.get_session_info.assert_called_with(mock_session)
        self.assertEqual(mock_session.last_check, mock_timezone.now.return_value)
        self.assertIsNone(mock_session.started)
        self.assertEqual(mock_session.stopped, mock_timezone.now.return_value)
