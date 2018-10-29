import datetime
import logging

from django.conf import settings
from django.db.models import (
    Model, OneToOneField, ForeignKey,
    CharField, DateTimeField, TextField,
    CASCADE, SET_NULL,
    Q
)
from django.shortcuts import reverse
from django.utils import timezone

from editors.models import Editor
from hosts.models import Host
from projects.models import Project

logger = logging.getLogger(__name__)

# Checkout status types
LAUNCHING = 'L'
OPEN = 'O'
CLOSED = 'C'
FAILED = 'F'
TERMINATED = 'T'

# Checkout event types
INFO = 'I'
START = 'S'
FINISH = 'F'
WARN = 'W'
ERROR = 'E'


class Checkout(Model):
    """Project checkout using an editor and execution host (if any)."""

    creator = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        related_name='checkouts_created',
        help_text='User who created the checkout'
    )

    created = DateTimeField(
        auto_now_add=True,
        help_text='When the checkout was created'
    )

    saved = DateTimeField(
        null=True,
        blank=True,
        help_text='When the checkout was saved'
    )

    closed = DateTimeField(
        null=True,
        blank=True,
        help_text='When the checkout was closed'
    )

    status = CharField(
        max_length=1,
        choices=(
            (LAUNCHING, 'Launching'),
            (OPEN, 'Open'),
            (CLOSED, 'Closed'),
            (FAILED, 'Failed'),
            (TERMINATED, 'Terminated')
        ),
        help_text='Status of the checkout'
    )

    project = ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='checkouts'
    )

    editor = OneToOneField(
        Editor,
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='checkout'
    )

    host = OneToOneField(
        Host,
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='host'
    )

    @staticmethod
    def create(project, creator):
        # If the project argument is an integer then get
        # project by `id`, otherwise by `address`
        try:
            project_id = int(project)
        except ValueError:
            project_id = None
        if project_id:
            project = Project.objects.get(id=project_id)
        else:
            project = Project.objects.get(address=project)

        # Check that there are no open checkouts for the
        # project (for some projects/editors/permissions this may be
        # able to be relaxed in the future)
        checkouts_open = Checkout.objects.filter(
            Q(project=project) &
            (Q(status=OPEN) | Q(status=LAUNCHING))
        )
        if checkouts_open:
            # TODO Terminate the open checkout if they have not been `saved`
            # for more than a certain period of time
            checkout = checkouts_open[0]
            raise CheckoutCreateError(
                type='exists',
                message='You already have a checkout open for this project',
                data={'url': checkout.editor.url}
            )

        # Currently, create a native editor
        # In the future, this the editor class might be chosen
        # by the user
        editor = Editor.create('native')

        # Currently, create a native execution host
        # In the future, this the editor class might be chosen
        # by the user
        host = Host.create('native')

        return Checkout.objects.create(
            project=project,
            editor=editor,
            host=host,
            creator=creator
        )

    @staticmethod
    def obtain(pk, user):
        """TODO: Check that the user has access to this checkout."""
        return Checkout.objects.get(pk=pk)

    def json(self):
        return {
            'id': self.id,
            'projectId': self.project.id if self.project else None,
            'hostUrl': self.host.url(),
            'hostToken': self.host.token(),
            'editorUrl': self.editor.url,
            'status': self.status,
            'events': list(self.events.all().values())
        }

    def get_absolute_url(self):
        return reverse('checkout_read', args=[self.pk])

    def get_callback_url(self):
        return settings.CALLBACK_URL + self.get_absolute_url()

    def event(self, type, topic, message, data=None):
        """"""
        # Format the message using the data
        if data:
            message = message.format(**data)

        # Record the event so it can be retrieved
        # by client polling
        CheckoutEvent.objects.create(
            checkout=self,
            type=type,
            topic=topic,
            message=message
        )

        if type == ERROR:
            # Log the error
            logger.error(message, exc_info=True, extra=data)

            # Set checkout's status to fail
            self.status = FAILED
            self.save()

    def open(self):
        """Open the checkout by pulling from the project and pushing to the editor."""
        self.status = LAUNCHING
        self.save()

        try:
            archive = self.project.pull()
            self.event(FINISH, 'project:pull', 'Pulled files from project')
        except Exception as error:
            return self.event(ERROR, 'project:pull', 'Error pulling files from project: ' + repr(error))

        try:
            self.editor.push(archive)
            self.event(FINISH, 'editor:push', 'Pushed files to editor')
        except Exception as error:
            return self.event(ERROR, 'editor:push', 'Error pushing files to editor: ' + repr(error))

        if self.status != FAILED:
            self.status = OPEN

        self.save()

    def save_(self):
        """
        Save the checkout by pulling from the editor and pushing to the project. 
        
        Underscore suffix to avoid name clash.
        """
        if self.status == OPEN:
            try:
                archive = self.editor.pull()
                self.project.push(archive)

                # Record the last time this was saved
                self.saved = datetime.datetime.now(tz=timezone.utc)
                self.save()
            except Exception as error:
                return self.event(ERROR, 'save', 'Error saving checkout: ' + repr(error))

    def close(self):
        """Close the checkout, allowing the project to be opened by others."""
        if self.status == OPEN:
            # Catch errors to ensure that this is always closed
            try:
                self.save_()
            except Exception as error:
                return self.event(ERROR, 'close', 'Error closing checkout: ' + repr(error))

            self.status = CLOSED
            self.closed = datetime.datetime.now(tz=timezone.utc)
            self.save()


class CheckoutCreateError(RuntimeError):

    def __init__(self, type, message, data):
        self.type = type
        self.message = message
        self.data = data

    def serialize(self):
        return {
            'type': self.type,
            'message': self.message,
            'data': self.data
        }


class CheckoutEvent(Model):
    """
    An event ocurring on a checkout.

    These are used to inform user of progress in launching the checkout.
    """

    checkout = ForeignKey(
        Checkout,
        on_delete=CASCADE,
        related_name='events',
        help_text='Checkout that this event relates to'
    )

    time = DateTimeField(
        auto_now_add=True,
        help_text='When this event was created'
    )

    type = CharField(
        max_length=1,
        choices=(
            (INFO, 'Info'),
            (START, 'Start'),
            (FINISH, 'Finish'),
            (WARN, 'Warning'),
            (ERROR, 'Error')
        ),
        help_text='Type of event'
    )

    topic = CharField(
        max_length=32,
        help_text='Topic of event'
    )

    # Note: ideally we would use the Postgres JSONField here for
    # better query support.
    # See https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#jsonfield
    # However, that can not be used with SQLIte suring development so
    # at present we stick with a TextField
    data = TextField(
        help_text='Data associated with the event, serialised as JSON'
    )

    message = TextField(
        help_text='Event message designed for user consumption'
    )
