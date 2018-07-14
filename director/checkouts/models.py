import time

from django.db.models import (
    Model, ForeignKey,
    CharField, DateTimeField, IntegerField, TextField,
    CASCADE, SET_NULL
)

from projects.models import Project
from editors.models import Editor

INFO = 'I'
START = 'S'
FINISH = 'F'
WARN = 'W'
ERROR = 'E'


class Checkout(Model):
    """
    A checkout of a project using a particular editor and
    execution host (if any).
    """

    creator = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        editable=False,
        related_name='checkouts_created',
        help_text='User who created the checkout'
    )

    created_at = DateTimeField(
        auto_now_add=True,
        help_text='When this event was created'
    )

    status = CharField(
        max_length=1,
        choices=(
            ('L', 'Launching'),
            ('O', 'Open'),
            ('C', 'Closed'),
            ('F', 'Failed'),
        ),
        help_text='Status of the checkout'
    )

    project = ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=SET_NULL
    )

    editor = ForeignKey(
        Editor,
        null=True,
        blank=True,
        on_delete=SET_NULL
    )

    @staticmethod
    def create(project):
        if type(project) is str:
            try:
                project = Project.objects.get(pk=project)
            except Project.DoesNotExist as error:
                raise error

        return Checkout.objects.create(
            project=project
        )

    @staticmethod
    def obtain(pk, user):
        """
        TODO: Check that the user has access to this checkout
        """
        return Checkout.objects.get(pk=pk)

    def json(self):
        return {
            'id': self.id,
            'project': self.project.id if self.project else None,
            'status': self.status,
            'events': list(self.events.all().values())
        }

    def event(self, type, topic, message, data=None):
        """
        """
        if data:
            message = message.format(**data)

        CheckoutEvent.objects.create(
            checkout=self,
            type=type,
            topic=topic,
            message=message
        )

        if type == ERROR:
            self.status = 'F'
            self.save()

    def launch(self):
        self.status = 'L'
        self.save()

        self.event(START, 'project:pull', 'Pulling files from project')
        try:
            time.sleep(3)
            archive = self.project.pull()
            self.event(FINISH, 'project:pull', 'Pulled files from project')
        except Exception as error:
            self.event(ERROR, 'project:pull', str(error))

        self.event(START, 'editor:push', 'Pushing files to editor')
        try:
            time.sleep(3)
            self.event(FINISH, 'editor:push', 'Pushed files to editor')
        except Exception as error:
            self.event(ERROR, 'editor:push', str(error))

        self.save()


class CheckoutEvent(Model):
    """
    An event ocurring on a checkout.

    These are used to inform user of progress in launching
    the checkout.
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
    # better query support. See https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#jsonfield
    # However, that can not be used with SQLIte suring development so
    # at present we stick with a TextField
    data = TextField(
        help_text='Data associated with the event, serialised as JSON'
    )

    message = TextField(
        help_text='Event message designed for user consumption'
    )
