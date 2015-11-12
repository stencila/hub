from __future__ import unicode_literals

import json
import httplib
import datetime
from collections import OrderedDict

import logging
logger = logging.getLogger('sessions')

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import PermissionDenied

import pytz

from components.models import Component
from users.models import User, UserToken
from accounts.models import Account

from sessions_.providers import providers


class Worker(models.Model):
    '''
    A computer running a Stencila session agent
    '''

    provider = models.CharField(
        choices=[(code, provider.__class__.__name__) for code, provider in providers.items()],
        max_length=16,
        null=True,
        help_text="The provider (e.g. Amazon EC2) for the worker"
    )

    provider_id = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="The provider specific identifier for the worker. Set when started."
    )

    # Use CharField instead of IPAddressField because of this issue:
    # https://code.djangoproject.com/ticket/5622#comment:61
    ip = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text="IP address of the worker. Set when started."
    )

    port = models.IntegerField(
        default=7320,
        null=True,
        blank=True,
        help_text="Port number of the session agent on the worker. "
                  "This usually should not be changed from the default value."
    )

    # The following fields are set in the self.start(), self.update()
    # and self.stop() methods below

    active = models.NullBooleanField(
        default=None,
        null=True,
        help_text="Indicates if the worker is active or not."
    )

    started = models.DateTimeField(
        null=True,
        help_text="Time that the worker was started"
    )

    updated = models.DateTimeField(
        null=True,
        help_text="Time that the worker information was last updated"
    )

    stopped = models.DateTimeField(
        null=True,
        help_text="Time that the worker was stopped"
    )

    def __unicode__(self):
        return 'Worker#%s' % (self.id)

    ################################################################
    # Communication method
    #
    # For talking to the actual worker machine

    def request(self, resource, method, data=None):
        '''
        Request a POST, GET or DELETE from the agent on this Worker
        '''
        assert self.ip is not None
        connection = httplib.HTTPConnection(self.ip, self.port)
        if data is not None:
            data = json.dumps(data)
        connection.request(method, resource, data, {
            "Content-type": "application/json",
            "Accept": "application/json"
        })
        response = connection.getresponse()
        if response.status == 200:
            return json.loads(response.read())
        else:
            raise Exception(response.read())

    ################################################################
    # Whole machine related methods
    #
    # For launching, terminating etc

    def launch(self):
        '''
        Launch this worker
        '''
        if self.started is None:
            providers[self.provider].launch(self)

            self.started = timezone.now()
            self.active = True
            self.save()

        return self

    def update(self):
        '''
        Get information on this worker
        '''
        stats = self.request('/stats', 'GET')
        worker_stats = WorkerStats()
        worker_stats.record(self, stats)

        self.updated = timezone.now()
        self.active = True
        self.save()

        return self

    def terminate(self):
        '''
        Stop this worker
        '''
        if self.started and self.active and self.stopped is None:
            self.update()
            providers[self.provider].terminate(self)

            self.stopped = timezone.now()
            self.active = False
            self.save()

        return self

    @staticmethod
    def choose(memory, cpu):
        '''
        Choose the best worker to launch a session on.

        Currently, very naive (just use the first worker.
        In the future could use `WorkerStats`
        data and an algorithm to determine the best one to start a session on
        '''
        workers = Worker.objects.filter(active=True)
        if len(workers) == 0:
            # If there are no active workers then launch one.
            # In production use EC2 in development VirtualBox
            provider = 'ec2' if settings.MODE == 'prod' else 'vbox'
            worker = Worker(provider=provider)
            worker.launch()
            return worker
        else:
            return workers[0]

    ################################################################
    # Session related methods
    #
    # For starting, stopping etc sessions
    # Mostly thin wrappers around `self.request()`

    def start(self, session):
        '''
        Start a session on this worker
        '''
        return self.request('/start', 'POST', {
            'image':    session.image,
            'command':  session.command,
            'memory':   session.memory,
            'cpu':      session.cpu,
            'token':    session.token
        })

    def get(self, session):
        '''
        Get a description of a session on this worker
        '''
        assert session.uuid is not None
        desc = self.request('/get/%s' % session.uuid, 'GET')
        # If agent returns an empty list it means that no session
        # with matching uuid exists on that worker
        if type(desc) is list and len(desc) == 0:
            return None
        return desc

    def stats(self, session):
        '''
        Get detailed stats on a session on this worker
        '''
        assert session.uuid is not None
        return self.request('/stats/%s' % session.uuid, 'GET')

    def logs(self, session):
        '''
        Get logs for a session on this worker
        '''
        assert session.uuid is not None
        return self.request('/logs/%s' % session.uuid, 'GET')

    def stop(self, session):
        '''
        Stop a session on this worker
        '''
        assert session.uuid is not None
        return self.request('/stop/%s' % session.uuid, 'DELETE')


class WorkerStats(models.Model):
    '''
    Timestamped information about the worker
    '''

    class Meta:
        verbose_name = "Worker stats"
        verbose_name_plural = "Worker stats"

    worker = models.ForeignKey(
        Worker,
        related_name='stats',
        null=True,
        help_text='Worker that the information relates to'
    )

    # The following fields are obtained from the worker machine.
    # The fields should be kept the same as those returned
    # by GET /info as coded in the agent.py file (although it
    # may send back other fields (e.g. ip and port) which do
    # not need to be not recorded here).

    stats_fields = (
        'time', 'sessions', 'users', 'processes', 'cpu_percent',

        'cpu_user', 'cpu_system', 'cpu_idle', 'cpu_nice', 'cpu_iowait', 'cpu_irq', 'cpu_softirq',

        'mem_total', 'mem_available', 'mem_percent', 'mem_used', 'mem_free',
        'mem_active', 'mem_inactive', 'mem_cached',

        'swap_total', 'swap_used', 'swap_free', 'swap_percent', 'swap_sin', 'swap_sout',

        'disk_use_total', 'disk_use_used', 'disk_use_free', 'disk_use_percent',
        'disk_io_read_count', 'disk_io_write_count', 'disk_io_read_bytes',
        'disk_io_write_bytes', 'disk_io_read_time', 'disk_io_write_time',

        'net_io_bytes_sent', 'net_io_bytes_recv', 'net_io_packets_sent', 'net_io_packets_recv',
        'net_io_errin', 'net_io_errout', 'net_io_dropin', 'net_io_dropout',
    )

    time = models.DateTimeField(null=True)
    sessions = models.IntegerField(null=True)
    users = models.TextField(null=True)
    processes = models.IntegerField(null=True)
    cpu_percent = models.FloatField(null=True)
    cpu_user = models.FloatField(null=True)
    cpu_system = models.FloatField(null=True)
    cpu_idle = models.FloatField(null=True)
    cpu_nice = models.FloatField(null=True)
    cpu_iowait = models.FloatField(null=True)
    cpu_irq = models.FloatField(null=True)
    cpu_softirq = models.FloatField(null=True)
    mem_total = models.FloatField(null=True)
    mem_available = models.FloatField(null=True)
    mem_percent = models.FloatField(null=True)
    mem_used = models.FloatField(null=True)
    mem_free = models.FloatField(null=True)
    mem_active = models.FloatField(null=True)
    mem_inactive = models.FloatField(null=True)
    mem_cached = models.FloatField(null=True)
    swap_total = models.FloatField(null=True)
    swap_used = models.FloatField(null=True)
    swap_free = models.FloatField(null=True)
    swap_percent = models.FloatField(null=True)
    swap_sin = models.FloatField(null=True)
    swap_sout = models.FloatField(null=True)
    disk_use_total = models.FloatField(null=True)
    disk_use_used = models.FloatField(null=True)
    disk_use_free = models.FloatField(null=True)
    disk_use_percent = models.FloatField(null=True)
    disk_io_read_count = models.FloatField(null=True)
    disk_io_write_count = models.FloatField(null=True)
    disk_io_read_bytes = models.FloatField(null=True)
    disk_io_write_bytes = models.FloatField(null=True)
    disk_io_read_time = models.FloatField(null=True)
    disk_io_write_time = models.FloatField(null=True)
    net_io_bytes_sent = models.FloatField(null=True)
    net_io_bytes_recv = models.FloatField(null=True)
    net_io_packets_sent = models.FloatField(null=True)
    net_io_packets_recv = models.FloatField(null=True)
    net_io_errin = models.FloatField(null=True)
    net_io_errout = models.FloatField(null=True)
    net_io_dropin = models.FloatField(null=True)
    net_io_dropout = models.FloatField(null=True)

    def record(self, worker, stats):
        self.worker = worker
        for field in self.stats_fields:
            setattr(self, field, stats[field])
        self.save()


class Session(models.Model):
    '''
    Every session must be linked to a User so that authorization to acess components can
    be determined.

    Users can "invite" other users to join a session. The invitee will have access to everything that the
    user has access to.
    '''

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    created = models.DateTimeField(
        auto_now_add=True,
        null=True,
        help_text='When this session was created'
    )

    account = models.ForeignKey(
        Account,
        null=True,
        help_text='Account that this session is linked to. Usually not null.',
        related_name='sessions'
    )

    component = models.ForeignKey(
        Component,
        null=True,
        help_text='Component for this session. Usually not null.',
        related_name='sessions'
    )

    user = models.ForeignKey(
        User,
        help_text='User for this session',
        related_name='sessions'
    )

    token = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text='User token used to sigin from the session',
    )

    image = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='Image for this session',
    )

    command = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='Image for this session',
    )

    memory = models.CharField(
        max_length=8,
        null=True,
        default='1g',
        help_text='Memory limit for this session. Format: <number><optional unit>, where unit = b, k, m or g',
    )

    cpu = models.IntegerField(
        null=True,
        default=1024,
        help_text='CPU share for this session. Share out of 1024',
    )

    worker = models.ForeignKey(
        Worker,
        null=True,
        blank=True,
        help_text='Worker that this session is running on',
        related_name='sessions'
    )

    uuid = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text='Unique identifier for the session'
    )

    port = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text='Port number for the session on the worker'
    )

    status = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text='Current status'
    )

    started_on_worker = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this session started on worker'
    )

    active = models.NullBooleanField(
        default=None,
        null=True,
        blank=True,
        help_text="Indicates if the session is active or not."
    )

    ready = models.NullBooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Indicates if the session is ready to be connected to"
    )

    started = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this session started'
    )

    updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this session had its information last updated'
    )

    stopped = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this session was stopped'
    )

    def __unicode__(self):
        return 'Session#%s' % (self.id)

    @property
    def url(self):
        return 'https://api.stenci.la/session/%i' % self.id

    @property
    def websocket(self):
        if self.ready:
            if settings.MODE == 'local':
                return 'ws://%s:%s/%s' % (self.worker.ip, self.port, self.component.address)
            else:
                return'wss://api.stenci.la/session/%s/connect' % (self.id)
        else:
            return None

    def serialize(self, request):
        '''
        Serialize this session
        '''
        return OrderedDict([
            ('id', self.id),
            ('url', self.url),
            ('websocket', self.websocket),
            ('ready', self.ready),
            ('status', self.status)
        ])

    @staticmethod
    def get_or_launch(component, user):
        '''
        Get an active session for the componet/user pair,
        or else launch one
        '''
        try:
            return Session.objects.get(
                component=component,
                user=user,
                active=True
            )
        except Session.DoesNotExist:
            return Session.launch(
                component=component,
                user=user,
            )

    @staticmethod
    def launch(component, user, account=None):
        '''
        Create and start a session
        '''
        # If account not supplied then get user's
        # current one
        if account is None:
            account = user.details.account()
        # Check that the user has rights to
        # create a session for that account
        Account.authorize_or_raise(user, account, CREATE, 'session')
        # Check the account has enough credit to create the session
        memory = 512  # For now just used a fixed memory size in megabytes
        account.enough_or_raise(memory=memory)
        # Create the session
        session = Session.objects.create(
            account=account,
            component=component,
            user=user,
            memory='%sm' % memory
        )
        # Start the session
        session.start()
        return session

    def start(self):
        '''
        Start the session. This is a separate method from `launch`
        because it is useful for testing when you want to create a
        session in the admin and start it from there
        '''
        if self.started is None:
            # Get the sessions token for the user, creating
            # one if necessary
            self.token = UserToken.get_sessions_token(self.user).string
            # Determine the image to use, based on the component
            # `envir` field.
            # Currently, all components use the r environment by default
            # but this will be customised later
            self.image = 'stencila/ubuntu-14.04-r-3.2'
            # Generate the run command for the image
            self.command = 'stencila-r "%s" serve:Inf' % (
                self.component.address
            )
            # Find the best worker to start the session on
            # Currently this just chooses a random worker that is active
            self.worker = Worker.choose(
                memory=self.memory,
                cpu=self.cpu
            )
            # Start on the worker
            self.status = 'Starting'
            # Session could be started asynchronously but for now
            # it is started here
            result = self.worker.start(self)
            self.uuid = result['uuid']
            if result['warnings'] is not None:
                logger.warning(result['warnings'])
            # Update
            self.active = True
            self.started = timezone.now()
            self.save()

    def update(self):
        '''
        Update session status. This is intended for getting basic
        information about a session necessary for connecting to it.
        For more detailed monitoring see the `monitor()` method.
        '''
        if self.worker:
            result = self.worker.get(self)
            # If worker does not return details then assume inactive
            if result is None:
                self.active = False
            else:
                # If get an error then log it
                if result.get('error'):
                    logger.error(result['error'])
                    self.active = False
                # ...otherwise, update details
                else:
                    self.active = True
                    self.started_on_worker = datetime.datetime.strptime(
                        result.get('started'),
                        "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=pytz.UTC)
                    for attr in 'port', 'ready', 'status':
                        setattr(self, attr, result.get(attr))
            self.updated = timezone.now()
            self.save()

    def monitor(self):
        '''
        Get detailed statistics and logs for this session
        '''
        if self.worker:
            result = self.worker.stats(self)
            if result.get('error'):
                logger.error(result['error'])
                self.active = False
            else:
                stats = SessionStats()
                stats.record(
                    session=self,
                    stats=result
                )

            SessionLogs.objects.create(
                session=self,
                logs=self.worker.logs(self)['logs']
            )

            self.active = True
            self.updated = timezone.now()
            self.save()

    def stop(self):
        '''
        Stop this session
        '''
        if self.stopped is None:
            # Always get stats and logs before
            # stopping a session
            self.monitor()

            if self.worker:
                result = self.worker.stop(self)
                if result.get('ok') != 1:
                    raise Exception('Session may not have been stopped')

                self.active = False
                self.ready = False
                self.stopped = timezone.now()
                self.save()

    def invite(self, inviter, invitee):
        '''
        Invite another user to connect to this session
        '''
        if inviter != self.user:
            raise PermissionDenied()
        Invitation.objects.create(
            session=self,
            invitee=invitee
        )

    def uninvite(self, inviter, invitee):
        '''
        Uninvite an invitee
        '''
        if inviter != self.user:
            raise PermissionDenied()
        Invitation.objects.filter(
            session=self,
            invitee=invitee
        ).delete()

    def authorize(self, user):
        '''
        Authorize (or not) a user to read or connect
        to this session. A user is authorised if the session
        is theirs or if they hold an invitation
        '''
        if user == self.user:
            return True
        if user.invitations.filter(session=self).count() > 0:
            return True
        return False

    def authorize_or_raise(self, user):
        if not self.authorize(user):
            raise PermissionDenied()
        else:
            return True


class Invitation(models.Model):

    session = models.ForeignKey(
        Session,
        help_text='Session that this invitation realtes to',
        related_name='invitations'
    )

    invitee = models.ForeignKey(
        User,
        help_text='User invited to the session',
        related_name='invitations'
    )


class SessionStats(models.Model):
    '''
    Timestamped information about the session
    '''

    class Meta:
        verbose_name = "Session stats"
        verbose_name_plural = "Session stats"

    session = models.ForeignKey(
        Session,
        related_name='stats',
        null=True,
        help_text="Session that this information relates to"
    )

    data = models.TextField(
        null=True,
        help_text="Stats data (usually as JSON) with all stats provided by worker"
                  "but not necessarily recorded as a separate field in this table"
    )

    stat_fields = (
        'time',
        'cpu_user', 'cpu_system', 'cpu_total',
        'mem_rss', 'mem_vms'
    )

    time = models.DateTimeField(
        null=True,
        help_text="Time that this information relates to"
    )

    cpu_user = models.FloatField(
        null=True,
        help_text="Accumulated user CPU time for the session"
    )

    cpu_system = models.FloatField(
        null=True,
        help_text="Accumulated system CPU time for the session"
    )

    cpu_total = models.FloatField(
        null=True,
        help_text="Accumulated CPU time for the session"
    )

    mem_rss = models.FloatField(
        null=True,
        help_text="Memory held in RAM (RSS: resident set size)"
    )

    mem_vms = models.FloatField(
        null=True,
        help_text="Memory held in virtual memory (VMS: virtual memory size)"
    )

    def record(self, session, stats):
        self.session = session
        self.data = json.dumps(stats)
        self.time = datetime.datetime.strptime(
            stats.get('read').split('.')[0],
            "%Y-%m-%dT%H:%M:%S"
        ).replace(tzinfo=pytz.UTC)
        cpu = stats.get('cpu_stats').get('cpu_usage')
        self.cpu_user = cpu.get('usage_in_usermode')
        self.cpu_system = cpu.get('usage_in_kernelmode')
        self.cpu_total = cpu.get('total_usage')
        mem = stats.get('memory_stats').get('stats')
        self.mem_rss = mem.get('total_rss')
        self.mem_vms = mem.get('total_swap')
        self.save()


class SessionLogs(models.Model):
    '''
    Timestamped logs captured from the session
    '''

    class Meta:
        verbose_name = "Session logs"
        verbose_name_plural = "Session logs"

    session = models.ForeignKey(
        Session,
        related_name='logs',
        null=True,
        help_text="Session that this log capture relates to"
    )

    captured = models.DateTimeField(
        auto_now=True,
        null=True,
        help_text='When this log output was captured'
    )

    logs = models.TextField(
        null=True,
        help_text="Log output"
    )
