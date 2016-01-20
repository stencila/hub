from __future__ import unicode_literals

import string
import random
import httplib
import json
from collections import OrderedDict

from django.db import models, IntegrityError
from django.utils.text import slugify
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from users.models import User
from general.errors import Error
from sessions_.models import Session

# Actions
#
# Authorizations levels used for defining access rights for Addresses.
# These values should not be altered since the integers are stored in the database
# on Keys

NONE = 0
READ = 10
ANNOTATE = 20
UPDATE = 30
AUTHORIZE = 40
DELETE = 50
CREATE = 60


def action_string(action):
    return {
        NONE: 'NONE',
        READ: 'READ',
        ANNOTATE: 'ANNOTATE',
        UPDATE: 'UPDATE',
        AUTHORIZE: 'AUTHORIZE',
        DELETE: 'DELETE',
        CREATE: 'CREATE'
    }.get(action, 'NONE')

action_choices = [
    (action, action_string(action)) for action in
    NONE, READ, ANNOTATE, UPDATE, AUTHORIZE, DELETE, CREATE
]


def curator(method, **kwargs):
    '''
    Make a request to curator. Used by methods below to make
    remote method calls. Keyword arguments POSTed as a JSON object.
    See `curator/curator.py` for more details.
    Perhaps could be done aysnychronusly to a task queue
    '''
    if settings.CURATOR_STUB:
        return {}
    else:
        connection = httplib.HTTPConnection('10.0.1.50', 7310)
        connection.request('POST', method, json.dumps(kwargs), {
            "Content-type": "application/json",
            "Accept": "application/json"
        })
        response = connection.getresponse()
        if response.status == 200:
            return json.loads(response.read())
        else:
            raise Exception(response.read())


class Component(models.Model):

    '''
    A Stencila component (stencil, theme, dataset etc)
    '''

    address = models.ForeignKey(
        'Address',
        null=False,
        blank=False,
        help_text='Address of this component'
    )

    forkee = models.ForeignKey(
        'Component',
        null=True,
        blank=True,
        related_name='forkers',
        help_text='Component from which this component was forked'
    )

    ##############

    type = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text='Type of this component'
    )

    title = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text='A brief title for the component. Can be duplicated'
    )

    summary = models.TextField(
        null=True,
        blank=True,
        help_text='A summary of the component.'
    )

    initialised = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time that the repository for this component was last created"
    )

    updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time that the metadata on this component was last updated"
    )

    ##############

    published = models.BooleanField(
        default=False,
        help_text='Should this component be published in listings of components at an address?'
    )

    views = models.IntegerField(
        default=0,
        help_text='Number of views of this component.'
    )

    stars = models.IntegerField(
        default=0,
        help_text='Number of times this component has been starred'
    )

    forks = models.IntegerField(
        default=0,
        help_text='Number of times this component has been forked'
    )

    ##########################################################################
    # Serialization

    def __unicode__(self):
        return '%s#%s(%s)' % (
            self.type.title(),
            self.id,
            self.address.id
        )

    def serialize(self, user, detail=0):
        data = OrderedDict([
            ('id', self.id),
            ('address', self.address.serialize(user)),
            ('forkee', self.forkee.id if self.forkee else None),
            ('type', self.type),
            ('title', self.title),
            ('summary', self.summary),
            ('urls', {
                'absolute': self.absolute_url(),
                'tiny': self.tiny_url(),
            }),
            ('published', self.published),
            ('views', self.views),
            ('stars', self.stars),
            ('forks', self.forks),
        ])
        return data

    ##########################################################################
    # Saving

    def save(self, *args, **kwargs):
        '''
        Override `save()` for things that need to be initialised
        '''
        super(Component, self).save(*args, **kwargs)

    ##########################################################################
    # Access and authorization

    @staticmethod
    def get(id, user, action, address=None):
        '''
        Get a component, checking that the user has sufficient access to perform
        the action
        '''
        # Construct subquery that checks access rights
        if user.is_authenticated():
            access = (
                Q(address__keys__users=user) &
                Q(address__keys__action__gte=action)
            )
            if action == READ:
                access |= Q(address__public=True)
        else:
            if action == READ:
                access = Q(address__public=True)
            else:
                access = None
        # Get the component
        if access is None:
            component = None
        else:
            component = Component.objects.filter(
                (Q(id=id) | Q(address=address)) & access
            ).select_related().first()
        # Raise an error if the user does not have access rights
        if component is None:
            raise Component.UnavailableError(
                id=id,
                action=action,
                address=address
            )
        else:
            return component

    ##########################################################################
    # Listing

    @staticmethod
    def list(user, address=None, published=True, sort=None):
        '''
        Get a list of components that the user has at least
        READ access to optionally filtered with arguments.
        '''
        # Get all components that have an address that is public...
        query = Q(address__public=True)
        # or the user has a READ key for...
        if not user.is_anonymous:
            query |= Q(address__keys__users=user) & Q(address__keys__action__gte=READ)
        # Add additional filters
        if address is not None:
            if address.endswith('/*'):
                query &= Q(address__id__startswith=address[:-2])
            else:
                query &= Q(address=address)
        if published is not None:
            query &= Q(published=published)
        # Filter with select related
        components = Component.objects.filter(query).select_related()
        # Order using `sort`
        if sort is not None:
            components = components.order_by(sort)

        return components

    ##########################################################################
    # CRUD

    @staticmethod
    def create(user, address, type, public=True, init=True):
        '''
        Create a new component
        '''
        # Create a temporary address if necessary
        if address is None:
            address = user.username
            address += '/' + ''.join(random.SystemRandom().choice(
                string.ascii_lowercase + string.ascii_uppercase + string.digits
            ) for _ in range(12))
        # Is there a parent address against which auth and sufficient resources can
        # be checked (analagous to "does the directory exist where you want to create this file")
        parent = Address.parent(
            address=address
        )
        if parent is None:
            raise Component.AddressOrphanError(
                address=address
            )
        # Does the user have authorization to CREATE the component <type> at
        # the parent address
        parent.authorize_or_raise(
            user=user,
            type=type,
            action=CREATE
        )
        # Does the account which owns the ancestor <address> have sufficient
        # credits to create another <type>
        parent.account.sufficient_or_raise(
            type=type,
            public=public,
            quantity=1
        )
        # Create the address for the component
        try:
            address = Address.objects.create(
                id=address,
                account=parent.account,
                occupied=True
            )
        except IntegrityError:
            raise Component.AddressOccupiedError(
                address=address
            )
        # Create the component instance
        component = Component.objects.create(
            address=address,
            type=type
        )
        # Create the DELETE key for the creating user
        key = Key.objects.create(
            address=address,
            action=DELETE
        )
        key.users.add(user)
        # Create the component repository
        if init:
            component.initialise()

        return component

    @staticmethod
    def read_one(id, user):
        component = Component.get(
            id=id,
            user=user,
            action=READ
        )
        return component

    @staticmethod
    def update_one(id, user, data):
        component = Component.get(
            id=id,
            user=user,
            action=UPDATE
        )
        # Do the update on fields that are allowed to be changed
        # Currently none!
        for name in []:
            if name in data:
                setattr(component, name, data[name])
        component.save()
        return component

    @staticmethod
    def delete_one(id, user):
        component = Component.get(
            id=id,
            user=user,
            action=DELETE
        )
        component.delete()

    ##########################################################################
    # URLs

    def slug(self):
        '''
        Convert this component's title into a slug for use in a URL
        '''
        return slugify(unicode(self.title)) if self.title else ""

    def url(self):
        '''
        Canonical URL for this component

        The trailing slash and dash are important! The trailing slash (when no slug) ensures that
        the relative URLs in stencils work. The trailing dash (on the end of the slug) identifies this
        as a slug and not an address of some other component.
        '''
        url = '/%s/' % self.address.id
        slug = self.slug()
        if slug:
            url += '%s-' % slug
        return url

    def absolute_url(self):
        '''
        Canonical URL for this component
        '''
        return 'https://stenci.la%s' % self.url()

    def tiny_url(self):
        '''
        Create a tiny URL for this component
        '''
        return 'https://stenci.la/%s~' % Component.tiny_convert(self.id)

    def tiny_id(str):
        '''
        Get the id of a component from it's tiny URL
        '''
        return Component.tiny_convert(str)

    @staticmethod
    def tiny_convert(value):
        '''
        Convert an id integer into a tiny URL string
        and vice versa.

        Based on http://code.activestate.com/recipes/111286/
        '''
        if type(value) is not int:
            fromdigits = string.letters+string.digits
            todigits = string.digits
        else:
            fromdigits = string.digits
            todigits = string.letters+string.digits
        x = 0
        for digit in str(value):
            x = x * len(fromdigits) + fromdigits.index(digit)
        if x == 0:
            res = todigits[0]
        else:
            res = ''
            while x > 0:
                digit = x % len(todigits)
                res = todigits[digit] + res
                x = int(x / len(todigits))
        return int(res) if type(value) is str else res

    ##########################################################################
    # Repository actions

    def initialise(self):
        '''
        Create a repository for this component
        '''
        if not self.initialised:
            curator('init', type=self.type, address=self.address.id)
            self.initialised = timezone.now()
            self.save()

    def update(self):
        '''
        Update metadata on the component by extracting it from its repository
        '''
        meta = curator('meta', address=self.address.id)
        self.type = meta.get('type', '')
        self.title = meta.get('title', '')
        self.summary = meta.get('summary', '')
        self.updated = timezone.now()
        self.save()

    def commits(self):
        '''
        Get a list of commits for this component
        '''
        return curator(
            'commits',
            address=self.address.id
        )

    ##########################################################################
    # Starring

    def star(self, user):
        '''
        Add this component as a favourite of the user.
        '''
        if not user.details.starreds.filter(id=self.id).count():
            user.details.starreds.add(self)
            self.stars += 1
            self.save()

    def unstar(self, user):
        '''
        Remove this component as a favourite of the user.
        '''
        if user.details.starreds.filter(id=self.id).count():
            user.details.starreds.remove(self)
            self.stars -= 1
            if self.stars < 0:
                self.stars = 0
            self.save()

    def starred(self, user):
        '''
        Has this component been favourited by the user?
        '''
        if not user.is_authenticated():
            return False
        return self.starrers.filter(user=user).exists()

    ##########################################################################
    # Forking

    def fork(self, user, to):
        '''
        Fork this component, creating a new component with address `to`
        '''
        # Create the fork
        fork = Component.create_one(
            user=user,
            address=to,
            type=self.type,
            init=False
        )
        # Get curator to do actual fork of repository
        curator(
            'fork',
            source=self.address,
            dest=fork.address
        )
        # Add to forkers
        self.forkers.add(fork)
        self.forks += 1
        self.save()

        return fork

    ##########################################################################
    # Sessions : active, deactivate etc

    def image(self):
        '''
        Get and image name that can be used to run this component
        '''
        #TODO : determine type of image to run in
        return 'stencila/ubuntu-14.04-r-3.2'

    def activate(self, user):
        # TODO store a link between component and session
        # (here linking session and image required by session)
        session = Session.get_or_launch(
            user=user,
            image=self.image()
        )
        # Start the session (may already be) and then wait until ready (may already be)
        session.start()
        session.wait()
        # Request the component so that it gets `Component::get()`ed into
        # the session
        session.request(
            verb='PUT',
            resource=self.address.id,
            method='grab'
        )
        return session

    def deactivate(self, user):
        session = Session.get_for(
            user=user,
            image=self.image()
        )
        if session:
            session.stop(
                user=user
            )
        return session

    def session(self, user, required=True):
        session = Session.get_for(
            user=user,
            image=self.image()
        )
        if required and session is None:
            raise Component.InactiveError(
                address=self.address.id,
                user=user
            )
        return session

    ##########################################################################
    # Content getting and saving

    def content_get(self, format):
        '''
        Get the content of this stencil
        '''
        assert self.type == 'stencil'
        assert format in ['html', 'cila']
        content = curator(
            'content',
            address=self.address.id,
            format=format
        )
        return content

    def content_set(self, user, format, content, revision):
        '''
        Set the content of this stencil
        '''
        assert self.type == 'stencil'
        assert format in ['html', 'cila']
        assert len(revision) == 40
        name = user.get_full_name()
        if not name or name.strip() == '':
            name = user.username
        result = curator(
            'save',
            address=self.address.id,
            format=format,
            content=content,
            revision=revision,
            author_name=name,
            author_email=user.email,
        )
        return result

    ##########################################################################
    # Errors

    class UnavailableError(Error):
        code = 404

        def __init__(self, id, action, address=None):
            self.id = id
            self.address = address
            self.action = action

        def serialize(self):
            return dict(
                error='component:unavailable',
                message='Component with this id does not exist or you do not have permission to perform this action on it',
                id=self.id,
                address=self.address,
                action=action_string(self.action)
            )

    class AddressOrphanError(Error):
        code = 400

        def __init__(self, address):
            self.address = address

        def serialize(self):
            return dict(
                error='component:address-orphan',
                message='The address does not have an ancestor address',
                address=self.address
            )

    class AddressOccupiedError(Error):
        code = 400

        def __init__(self, address):
            self.address = address

        def serialize(self):
            return dict(
                error='component:address-occupied',
                message='The address is already occupied by another component',
                address=self.address
            )

    class InactiveError(Error):
        code = 400

        def __init__(self, address, user):
            self.address = address
            self.user = user

        def serialize(self):
            return dict(
                error='component:inactive',
                message='This component is not currently activated by the user',
                address=self.address,
                user=self.user.username
            )

class Address(models.Model):

    id = models.CharField(
        primary_key=True,
        max_length=1024,
        help_text='Address string e.g. "pangea/swamp/pond'
    )

    account = models.ForeignKey(
        'accounts.Account',
        related_name='addresses',
        help_text='The account that owns this address'
    )

    public = models.BooleanField(
        default=True,
        help_text='Is this address publically readable?'
    )

    occupied = models.BooleanField(
        default=False,
        help_text='Is this address occupied by a component?'
    )

    ##########################################################################
    # Serialization

    def __unicode__(self):
        return 'Address#%s' % (
            self.id
        )

    def serialize(self, request):
        return OrderedDict([
            ('id', self.id),
            ('account', self.account.serialize(request)),
            ('public', self.public),
            ('occupied', self.occupied),
        ])

    ##########################################################################
    # Saving

    def save(self, *args, **kwargs):
        '''
        Override `save()` to ensure associated models have been
        created
        '''
        super(Address, self).save(*args, **kwargs)

    ##########################################################################
    # Listing

    @staticmethod
    def list(user, address='', occupied=False):
        '''
        Get a list of addresses that the user has access to

        This could be extended to include `Address`es that the user has READ or other
        access rights to. But for now, its just public one
        '''
        return Address.objects.filter(
            Q(id__startswith=address) & (
                Q(public=True) | (Q(keys__users=user) & Q(keys__action__gte=READ))
            ) &
            Q(occupied=occupied)
        ).select_related()

    ##########################################################################
    # CRUD

    @staticmethod
    def create_one(user, address, public=True, account=None):
        '''
        Create a new address
        '''
        from accounts.models import Account

        # Is this a child address or a root address?
        if address.find('/'):
            pass
        else:
            # For a root address the account argument needs to be given
            assert account is not None
            # Does the account exist?
            try:
                account_instance = Account.objects.get(name=account)
            except Account.DoesNotExist:
                raise Account.NonexistantError(name=account)
        # Is the user an account owner? (only owners can create an address)
        # TODO
        #raise Address.UnauthorisedError(account=account,action='create')
        # Does the account have sufficient resources to create a private address?
        if not public:
            # TODO
            raise Address.InsufficientError(account=account)
        # Does the address already exist?
        # TODO
        #raise Address.ExistsError(address=address)

        # Create the instance
        return Address.objects.create(
            address=address,
            account=account_instance
        )

    ##########################################################################
    # Authorization

    @staticmethod
    def parent(address):
        '''
        Get the parent address of an address.
        Return None if is there is no parent
        '''
        parts = address.split('/')
        parts.pop()
        id = '/'.join(parts)
        print address, parts, id
        try:
            return Address.objects.select_related().get(id=id)
        except Address.DoesNotExist:
            return None

    def authorize(self, user, type, action):
        '''
        Authorize a user to perform an action at an address.
        '''
        # If public then anyone can read
        if action == READ and self.public:
            return True
        # Account owner can do anything
        if self.account.owners.filter(
            id=user.id
        ).count():
            return True
        # Otherwise need to have a key
        if self.keys.filter(
            Q(action__gte=action) & (
                Q(type=type) | Q(type=None)
            ) &
            Q(users=user)
        ).count():
            return True

        return False

    def authorize_or_raise(self, user, type, action):
        '''
        Authorize a user to perform an action at an address or
        else raise an error.
        '''
        if self.authorize(user, type, action):
            return True
        else:
            raise Address.UnauthorizedError(
                address=self.id,
                type=type,
                action=action
            )

    ##########################################################################
    # Errors

    class UnauthorizedError(Error):
        code = 403

        def __init__(self, address, type, action):
            self.address = address
            self.type = type
            self.action = action

        def serialize(self):
            return dict(
                error='address:unauthorized',
                message='Not authorized to perform this action at this address',
                address=self.address,
                type=self.type,
                action=self.action
            )

    class ExistsError(Error):
        code = 400

        def __init__(self, address):
            self.address = address

        def serialize(self):
            return dict(
                error="address:exists",
                message='Address already exists',
                url='https://stenci.la/api/errors/address/exists',
                address=self.address
            )


class Key(models.Model):

    '''
    A Key provides access to one or more components.
    '''

    name = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text='A name for this key.'
    )

    address = models.ForeignKey(
        'Address',
        related_name='keys',
        help_text='The address this key gives access rights to.'
    )

    type_choices = [
        ('address', 'Address'),
        ('session', 'Session'),
        ('stencil', 'Stencil'),
        ('theme', 'Theme'),
    ]

    type = models.CharField(
        null=True,
        blank=True,
        choices=type_choices,
        max_length=32,
        help_text='The type of component or resource this key gives access rights to.'
        'If blank, gives access to all types of component.'
    )

    action = models.IntegerField(
        null=False,
        blank=False,
        choices=action_choices,
        help_text='The access right granted by this key to a component.'
    )

    users = models.ManyToManyField(
        User,
        related_name='keys',
        help_text='The users that hold this key'
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Notes about this key'
    )

    ##########################################################################
    # Serialization

    def __unicode__(self):
        return 'Key#%s(%s,%s)' % (
            self.id,
            self.address,
            action_string(self.action)
        )

    def serialize(self, request):
        return OrderedDict([
            ('id', self.id),
            ('name', self.name),
            ('notes', self.notes),
            ('address', self.address),
            ('type', self.type),
            ('action', self.action),
            ('users', [grantee.serialize(request) for grantee in self.users.all()]),
            ('account', self.account.serialize(request)),
        ])

    ##########################################################################
    # Listing

    @staticmethod
    def list_user(user):
        '''
        Get a list of keys for which the user is a grantee
        '''
        return Key.objects.filter(users__id__exact=user.id)

    @staticmethod
    def list_account(account):
        '''
        Get a list of keys for the account
        '''
        return Key.objects.filter(account__id__exact=account.id)

    ##########################################################################
    # CRUD

    @staticmethod
    def create_one(account, name, address, action, users):
        pass
