#  This file is part of Stencila Hub.
#  
#  Copyright (C) 2015-2016 Stencila Ltd.
#  
#  Stencila Hub is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Stencila Hub is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public License
#  along with Stencila Hub.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import json
import time
import datetime
from collections import OrderedDict

import logging
logger = logging.getLogger('sessions')

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_save
from django.dispatch import receiver

import pytz
import requests

from general.errors import Error
from users.models import User, UserToken

from sessions_.providers import providers
from builds.models import Build


class Worker(models.Model):
    '''
    A computer running a Stencila session agent
    '''

    cpus = models.FloatField(
        default=1,
        help_text='Number of CPUs/vCPUs'
    )

    memory = models.FloatField(
        default=1,
        help_text='Random access memory (RAM) in GB'
    )

    # Amount of memory (GB) reserved for running a worker
    # and which can't be allocated to sessions
    # See `choose()` method below.
    # Current value of 0.25GB chosen based on base memory usage
    # of existing workers ~0.18GB
    memory_reserved = 0.25

    storage = models.FloatField(
        default=10,
        help_text='Disk storage in GB'
    )

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
        if settings.WORKER_STUB:
            print 'WORKER_STUB is on; dummy response'
            return {
                'uuid': '------',
                'started': '0001-01-01T01:01:01Z'
            }
        else:
            response = requests.request(
                method,
                'http://%s:%s/%s' % (self.ip, self.port, resource),
                headers={
                    "Content-type": "application/json",
                    "Accept": "application/json"
                },
                json=data,
                # So, that this does not hang for a long time (e.g. if an error with worker) set a timeout
                # http://docs.python-requests.org/en/latest/user/advanced/#timeouts
                timeout=(10.1, 120.1)
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(response.text)

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
        if self.active:
            stats = self.request('info', 'GET')
            worker_stats = WorkerStats()
            worker_stats.record(self, stats)

            self.updated = timezone.now()
            self.active = True
            self.save()

        return self

    def pull(self, image=None):
        '''
        Pull Docker images from the Docker repository
        '''
        if self.active:
            self.request('pull', 'PUT', {
                'image': image
            })

        return self

    def terminate(self):
        '''
        Stop this worker
        '''
        if self.started and self.active and self.stopped is None:
            self.update()

            sessions = Session.objects.filter(worker=self)

            # Attempt to gracefully stop all sessions
            for session in sessions:
                session.stop(user='hub')

            # Actually terminate the machine
            providers[self.provider].terminate(self)

            # Ensure all sessions are now marked as inactive
            # (in case session.stop() failed)
            for session in sessions:
                session.active = False
                session.save()

            self.stopped = timezone.now()
            self.active = False
            self.save()

        return self

    @staticmethod
    def choose(session):
        '''
        Choose the best worker to launch a session.

        Selects the worker that can fit the session (given allocated CPU shares,
        memory etc) but which is most full. This is done to
        reduce the number of workers required by making best use of the available workers;
        workers that end up with no sessions can be terminated.
        '''
        # Select workers that have enough resources to fit session and choose
        # one with highest number of existing sessions. The memory buffer is
        # intended to ensure a worker's memory is not completely filled up with
        # sessions.
        # The `coalesce` is important otherwise get NULLs if no active sessions on
        # a worker which are all filtered out by WHERE
        workers = Worker.objects.raw('''
            SELECT
                id,
                coalesce(sessions,0) AS session_count,
                memory AS memory,
                coalesce(memory_alloc,0) AS memory_alloc,
                memory-coalesce(memory_alloc,0) AS memory_remain,
                cpus*100 AS cpu,
                coalesce(cpu_alloc,0) AS cpu_alloc,
                cpus*100-coalesce(cpu_alloc,0) AS cpu_remain
            FROM sessions__worker LEFT JOIN (
                SELECT
                    worker_id,
                    count(*) AS sessions,
                    sum(memory) AS memory_alloc,
                    sum(cpu) AS cpu_alloc
                FROM sessions__session
                WHERE active=true
                GROUP BY worker_id
            ) AS sessions_summary ON sessions__worker.id=sessions_summary.worker_id
            WHERE
                active = true AND
                (memory-coalesce(memory_alloc,0)-%f) > %f AND
                (cpus*100-coalesce(cpu_alloc,0)) > %f
            ORDER BY
                session_count DESC
        ;''' % (Worker.memory_reserved, session.memory, session.cpu))
        # Ensure `RawQuerySet` is executed before doing `len`
        workers = list(workers)
        if len(workers) == 0:
            raise Exception("Insuffient worker capacity")
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
        return self.request('start', 'POST', {
            'image':    session.image,
            'command':  session.command,
            'memory':   session.memory,
            'cpu':      session.cpu,
            'cpus':     self.cpus,
            'token':    session.token
        })

    def get(self, session):
        '''
        Get a description of a session on this worker
        '''
        assert session.uuid is not None
        desc = self.request('get/%s' % session.uuid, 'GET')
        # If agent returns an empty list it means that no session
        # with matching uuid exists on that worker
        if type(desc) is list and len(desc) == 0:
            return None
        return desc

    def stats_for(self, session):
        '''
        Get detailed stats on a session on this worker
        '''
        assert session.uuid is not None
        return self.request('stats/%s' % session.uuid, 'GET')

    def logs_for(self, session):
        '''
        Get logs for a session on this worker
        '''
        assert session.uuid is not None
        return self.request('logs/%s' % session.uuid, 'GET')

    def stop(self, session):
        '''
        Stop a session on this worker
        '''
        assert session.uuid is not None
        return self.request('stop/%s' % session.uuid, 'DELETE')


def workers_update():
    '''
    Update all workers that are currently active
    '''
    for worker in Worker.objects.filter(active=True):
        worker.update()


def workers_pull(image=None):
    '''
    Get all active workers to pull Docker images
    '''
    for worker in Worker.objects.filter(active=True):
        worker.pull(image)


@receiver(post_save, sender=Build)
def workers_build_post_save(sender, instance, created, **kwargs):
    '''
    Respond to an post_save signal from a build
    '''
    if created:
        if instance.package == 'docker':
            workers_pull(instance.flavour)


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


class SessionType(models.Model):

    rank = models.IntegerField(
        default=1,
        help_text='Nominal rank of session type (higher ~ more powerful)',
    )

    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text='Name of the session type',
    )

    description = models.TextField(
        null=False,
        blank=False,
        help_text='A short description of the session type',
    )

    memory = models.FloatField(
        default=1,
        null=False,
        blank=False,
        help_text='Gigabytes (GB) of memory allocated'
    )

    cpu = models.FloatField(
        default=1,
        null=False,
        blank=False,
        help_text='CPU shares (out of 100 per CPU) allocated'
    )

    network = models.FloatField(
        default=-1,
        null=False,
        blank=False,
        help_text='Gigabytes (GB) of network transfer allocated. -1 = unlimited'
    )

    lifetime = models.IntegerField(
        default=-1,
        null=False,
        blank=False,
        help_text='Minutes before the session is terminated. -1 = infinite.'
    )

    timeout = models.IntegerField(
        default=60,
        null=False,
        blank=False,
        help_text='Minutes of inactivity before the session is terminated'
    )

    number = models.IntegerField(
        default=-1,
        null=False,
        blank=False,
        help_text='Maximum number of this session type that can be running at one time. -1 = infinite.'
    )

    def serialize(self, *args, **kwargs):
        return OrderedDict([
            ('id', self.id),
            ('rank', self.rank),
            ('name', self.name),
            ('memory', self.memory),
            ('cpu', self.cpu),
            ('network', self.network),
            ('lifetime', self.lifetime),
            ('timeout', self.timeout),
            ('number', self.number),
        ])


class SessionImage(models.Model):

    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text='Name of the Docker image',
    )

    tag = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default='latest',
        help_text='Tag on the Docker image',
    )

    display_name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text='Name of the image as displayed',
    )

    def serialize(self, *args, **kwargs):
        return OrderedDict([
            ('id', self.id),
            ('name', self.name),
            ('tag', self.tag),
        ])


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
        'accounts.Account',
        null=True,
        blank=True,
        help_text='Account that this session is linked to. Usually not null.',
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

    image_model = models.ForeignKey(
        SessionImage,
        help_text='SessionImage for this session',
        related_name='sessions'
    )

    image = models.CharField(
        max_length=64,
        help_text='Image name string for this session. Redundant given image_model',
    )

    command = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default='stencila-session',
        help_text='Command to run the session in the Docker container',
    )

    type = models.ForeignKey(
        SessionType,
        help_text='SessionType for this session',
        related_name='sessions'
    )

    memory = models.FloatField(
        null=True,
        blank=True,
        help_text='Gigabytes (GB) of memory allocated. If left null will default to that of session type.',
    )

    cpu = models.FloatField(
        null=True,
        blank=True,
        help_text='CPU shares (out of 100 per CPU) allocated If left null will default to that of session type.',
    )

    network = models.FloatField(
        null=True,
        blank=True,
        help_text='Gigabytes (GB) of network transfer allocated. -1 = unlimited. If left null will default to that of session type.',
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

    pinged = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this session was last pinged by a client'
    )

    stopped = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this session was stopped'
    )

    def __unicode__(self):
        return 'Session#%s' % (self.id)

    def url(self):
        if settings.MODE == 'local':
            return '/sessions/%i' % self.id
        else:
            return 'https://stenci.la/sessions/%i' % self.id

    def websocket(self):
        if self.ready:
            if settings.MODE == 'local':
                return 'ws://%s:%s' % (self.worker.ip, self.port)
            else:
                return'wss://stenci.la/sessions/%s@connect' % (self.id)
        else:
            return None

    def serialize(self, user):
        '''
        Serialize this session
        '''
        return OrderedDict([
            ('id', self.id),
            ('local', False),
            ('user', self.user.serialize(user=user)),
            ('image', self.image_model.serialize()),
            ('type', self.type.serialize()),
            ('url', self.url()),
            ('websocket', self.websocket()),
            ('status', self.status),
            ('ready', self.ready),
            ('started', self.started),
            ('updated', self.updated),
            ('pinged', self.pinged),
            ('stopped', self.stopped)
        ])

    @staticmethod
    def list(user, filter={}):
        '''
        Get a list of sessions that the user owns
        '''
        if user.is_authenticated():
            filter.update({
                'user': user
            })
            return Session.objects.filter(**filter)
        else:
            return Session.objects.none()

    @staticmethod
    def get(id, user):
        '''
        Get a session, checking that the user is authorized
        to access it
        '''
        try:
            return Session.objects.get(
                id=id
            ).authorize_or_raise(user)
        except Session.DoesNotExist:
            raise Session.NotFoundError(
                id=id
            )

    @staticmethod
    def get_for(user, image_name):
        '''
        Get an active session for the user/image pair.
        In most cases user will only have one active session per user/image.
        But in cases that the user has more than one, currently just take the most recently started.
        '''
        return Session.objects.filter(
            user=user,
            image=image_name,
            active=True
        ).order_by('-started').first()

    @staticmethod
    def get_or_launch(user, image_name):
        '''
        Get an active session for the user/image pair,
        or else launch one
        '''
        current = Session.get_for(
            user=user,
            image_name=image_name
        )
        if current:
            return current
        else:
            return Session.launch(
                user=user,
                image_name=image_name
            )

    @staticmethod
    def launch(user, image_name, type_id=None, account=None):
        '''
        Create and start a session
        '''
        from accounts.models import Account

        # Get the session type
        if type_id is None:
            # If the session type is not specified (ie the accoun that owns the
            # component is not hosting it) then fallback to defaults based on
            # user type
            assert user.is_authenticated()
            if user.details.guest:
                type_id = 1
            else:
                type_id = 1
                # TODO fallback to default based on account type
                # user_account = Account.objects.filter(
                #     owners=user,
                #     personal=True
                # )
                # if user_account is None:
                #     type_id = 1
                # else:
                #     type_id = user_account.type.default_session.id
        type = SessionType.objects.get(
            id=type_id
        )

        # Check that the number of active sessions of this type does not
        # exceed the maximum
        if type.number > 0:
            count = Session.objects.filter(
                active=True,
                type=type
            ).count()
            if count >= type.number:
                # Log it and then raise an error
                logger.warning('Reached limit for session type', exc_info=True, extra=dict(
                    user=user,
                    type=type.name,
                    max=type.number,
                    count=count
                ))
                raise Session.TypeLimitError()

        # Get the session image
        image = SessionImage.objects.get(
            name=image_name
        )

        # Create and start the session
        session = Session.objects.create(
            account=account,
            user=user,
            image_model=image,
            image=image.name,
            type=type
        )
        session.start()

        return session

    def start(self):
        '''
        Start the session. This is a separate method from `launch`
        because it is useful for testing when you want to create a
        session in the admin and start it from there
        '''
        if self.started is None:
            # Just-in-time initalization of attributes required for running
            # a session (to save having to enter these in the admin)
            #
            # Get the sessions token for the user, creating
            # one if necessary
            self.token = UserToken.get_sessions_token(self.user).string
            # Apply session type limits to this session
            # is they have not bee cutomised
            if self.memory is None:
                self.memory = self.type.memory
            if self.cpu is None:
                self.cpu = self.type.cpu
            if self.network is None:
                self.network = self.type.network

            # If worker not yet assigned (eg. in admin)
            if not self.worker:
                # Find the best worker to start the session on
                self.worker = Worker.choose(self)

            # Start on the worker
            self.status = 'Starting'
            # Session could be started asynchronously but for now
            # it is started here
            result = self.worker.start(self)
            self.uuid = result.get('uuid')
            if result.get('warning'):
                logger.warning('Session start warning', exc_info=True, extra=dict(
                    session=self.id,
                    warning=result.get('warning')
                ))
            if result.get('error'):
                logger.error('Session start error', exc_info=True, extra=dict(
                    session=self.id,
                    error=result.get('error')
                ))

            # Update
            self.active = True
            self.started = timezone.now()
            self.save()

    def update(self, save=True):
        '''
        Update session status. This is intended for getting basic
        information about a session necessary for connecting to it.
        For more detailed monitoring see the `monitor()` method.

        @param save Should the update be saved to database (set to False if being
            called quickly)
        '''
        if self.worker:
            result = self.worker.get(self)
            # If worker does not return details then assume inactive
            if result is None:
                self.active = False
            else:
                # If get an error then log it
                if result.get('error'):
                    logger.error('session %s ; %s ' % (self.id, result.get('error')))
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
            if save:
                self.save()

    def wait(self, timeout=60):
        '''
        Wait until the session is ready.
        '''
        started = time.clock()
        while not self.ready:
            time.sleep(0.3)
            waited = time.clock()-started
            if waited > timeout:
                raise Session.TimeoutError(
                    waited=waited,
                    timeout=timeout
                )
            self.update(save=False)
            # Save, if gone from unready to ready
            if self.ready:
                self.save()

    def monitor(self):
        '''
        Get detailed statistics and logs for this session
        '''
        if self.worker and self.active:
            result = self.worker.stats_for(self)
            if result.get('error'):
                logger.error(result.get('error'))
                self.active = False
            else:
                stats = SessionStats()
                stats.record(
                    session=self,
                    stats=result
                )

            SessionLogs.objects.create(
                session=self,
                logs=self.worker.logs_for(self).get('logs')
            )

            self.active = True
            self.updated = timezone.now()
            self.save()

    def request(self, resource, verb='GET', method=None, data=None):
        '''
        Pass an HTTP request on to the session
        '''
        if self.active:
            if self.ready:
                # Update ping time
                self.ping()
                # Construct URL
                url = 'http://%s:%s/%s' % (self.worker.ip, self.port, resource)
                if method:
                    url += '@%s' % method
                # If data is string send it as a string, otherwise send it as JSON
                if data and type(data) is not str:
                    data = json.dumps(data)
                response = requests.request(
                    verb,
                    url,
                    headers={
                        "Content-type": "application/json",
                        "Accept": "application/json"
                    },
                    data=data,
                    # So, that this does not hang for a long time (e.g. if an error with session) set a timeout
                    # http://docs.python-requests.org/en/latest/user/advanced/#timeouts
                    # Tuple of (connect, read) timeouts
                    timeout=(10.1, 300.1)
                )
                # Always pass though the response code and content
                # but log 5xx errors and ensure a JSON object.
                status = response.status_code
                body = response.text
                if status >= 500:
                    logger.error('session %s ; status %s; %s ' % (self.id, status, body))
                    # This method is expected to return a JSON string, so ensure that is the case
                    # for errors (status codes <500 are assumed to behave as expected and provide JSON)
                    try: 
                        error = json.loads(body)
                    except: 
                        # The `session:request-proxy` error ID is use to distinguish this wrapping
                        # from a `session:internal` error
                        error = {
                            'error': 'session:request-proxy',
                            'message': body
                        }
                    body = json.dumps(error)
                return (status, body)
            else:
                raise Session.NotReadyError(self.id)
        else:
            raise Session.NotActiveError(self.id)

    def ping(self):
        '''
        Receive a ping from the client
        '''
        self.pinged = timezone.now()
        self.save()

    def stop(self, user):
        '''
        Stop this session

        `user` should be supplied for authorization but set to `"hub"`
        if this session is being stopped by the hub itself (see `vacuum` below)
        '''
        if user != 'hub':
            if user != self.user:
                raise Session.UnauthorizedError(
                    session=self,
                    action='stop'
                )

        if self.stopped is None and self.worker:

            try:
                # Always get stats and logs before
                # stopping a session
                self.monitor()

                # Attempt to stop
                result = self.worker.stop(self)
                if result.get('ok') != 1:
                    raise Exception('Session may not have been stopped')

            except Exception, e:
                logger.error('Error stopping session', exc_info=True, extra=dict(
                    session=self.id
                ))

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
        if user.is_authenticated():
            if user == self.user:
                return True
            if user.invitations.filter(session=self).count() > 0:
                return True
        return False

    def authorize_or_raise(self, user):
        if not self.authorize(user):
            raise Session.NotFoundError(id=self.id)
        else:
            return self

    ##########################################################################
    # Errors

    class TypeLimitError(Error):
        code = 404

        def __init__(self, type):
            self.type = type

        def serialize(self):
            return dict(
                error='session:type-limit',
                message='The limit for this number of sessions has been reached. Please wait for an available slot, or launch a different type of session',
                type=self.type.name
            )


    class NotFoundError(Error):
        code = 404

        def __init__(self, id):
            self.id = id

        def serialize(self):
            return dict(
                error="session:not-found",
                message='Session with this id does not exist or you do not have permission to access it',
                id=self.id
            )

    class NotActiveError(Error):
        code = 400

        def __init__(self, session):
            self.session = session

        def serialize(self):
            return dict(
                error="session:not-active",
                message='Session is no longer active',
                session=self.session
            )

    class NotReadyError(Error):
        code = 400

        def __init__(self, session):
            self.session = session

        def serialize(self):
            return dict(
                error="session:not-ready",
                message='Session is not yet ready',
                session=self.session
            )

    class TimeoutError(Error):
        code = 504

        def __init__(self, waited, timeout):
            self.waited = waited
            self.timeout = timeout

        def serialize(self):
            return dict(
                error="session:timeout",
                message='Timed out waiting for session to be ready',
                waited=self.waited,
                timeout=self.timeout
            )

def sessions_vacuum():
    '''
    Stop sessions which have exceeded their lifetime or
    have timedout (i.e. have not been pinged in within `timeout`)
    '''
    now = timezone.now()
    for session in Session.objects.filter(active=True):
        since_started = now-session.started if session.started else None
        since_pinged = now-session.pinged if session.pinged else None
        lifetime = datetime.timedelta(minutes=session.type.lifetime)
        timeout = datetime.timedelta(minutes=session.type.timeout)

        stop = False

        if session.type.lifetime > 0:
            if since_started is not None and since_started > lifetime:
                stop = True

        if session.type.timeout > 0:
            if since_pinged is not None:
                # Started and pinged
                if since_pinged > timeout:
                    stop = True
            else:
                # Started and never been pinged...
                if since_started is not None and since_started > timeout:
                    stop = True

        if stop:
            session.stop(
                user='hub'
            )


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
