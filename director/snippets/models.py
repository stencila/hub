from __future__ import unicode_literals
from collections import OrderedDict

from django.db import models
from django.utils import timezone

import jsonfield

from general.errors import Error
from users.models import User, UnauthenticatedError


class Snippet(models.Model):
    '''
    A snippet
    '''

    id = models.CharField(
        primary_key=True,
        max_length=64,
        null=False,
        blank=False,
        help_text='The id'
    )

    spec = jsonfield.JSONField(
        default='{}', # Seems to be necessary to have valid JSON for initial creation of a snippet in admin
        null=False,
        blank=False,
        help_text='Flavour of the package (e.g. 3.2 for R package, ubuntu-14.04-r-3.2 for Docker image)',
        load_kwargs={
            'object_pairs_hook': OrderedDict
        }
    )

    # Meta data fields

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        help_text='User that last created or updated this snippet'
    )

    datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date/time that this snippet was created or updated'
    )

    def serialize(self, user, detail=1):
        '''
        Serialize this snippet
        '''
        if detail==1:
            return self.spec
        else:
            return OrderedDict([
                ('id', self.id),
                ('summary', self.spec.get('summary'))
            ])

    @staticmethod
    def list():
        '''
        List and search for snippets
        '''
        return Snippet.objects.all()

    @staticmethod
    def get(id):
        '''
        Get a snippet
        '''
        try:
            snippet = Snippet.objects.get(id=id)
        except:
            raise Snippet.NotFoundError(id=id)
        return snippet

    @staticmethod
    def put(user, id, spec):
        '''
        Create a new snippet or update an existing one
        '''
        if not user.is_authenticated():
            raise UnauthenticatedError()

        if not user.details.builder:
            raise Snippet.UnauthorizedError(user=user)

        if spec.get('id') != id:
            raise Snippet.InvalidError(
                message='The `id` field in the snippet does not match the requested `id`'
            )

        # TODO further validation of the spec
        
        snippet, created = Snippet.objects.get_or_create(id=id)

        # TODO set searchable fields e.g. summary, notes
        
        snippet.spec = spec
        snippet.user = user
        snippet.datetime = timezone.now()
        snippet.save()

        return snippet

    class UnauthorizedError(Error):
        code = 403

        def __init__(self, user):
            self.user = user

        def serialize(self):
            return dict(
                error='snippet:unauthorized',
                message='User is not authorized to create or update snippets',
                user=self.user.username
            )

    class NotFoundError(Error):
        code = 404

        def __init__(self, id):
            self.id = id

        def serialize(self):
            return dict(
                error='snippet:not-found',
                message='Snippet with `id` was not found',
                id=self.id
            )

    class InvalidError(Error):
        code = 400

        def __init__(self, message):
            self.message = message

        def serialize(self):
            return dict(
                error='snippet:invalid',
                message=self.message
            )