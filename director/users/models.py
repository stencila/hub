from __future__ import unicode_literals

from collections import OrderedDict

import time
import datetime
import pytz
import base64

import Crypto.Cipher
import Crypto.Random

from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login

import jsonfield

from general.errors import Error


class UnauthenticatedError(Error):
    '''
    Used when user needs to be authenticated
    '''

    code = 401

    def serialize(self):
        return dict(
            error='user:unauthenticated',
            message='User is not authenticated'
        )


class UserDetails(models.Model):
    '''
    Additional details for a user not available on contrib.auth.models.User.

    Following this https://docs.djangoproject.com/en/1.9/topics/auth/customizing/#specifying-a-custom-user-model
    advice not deriving from a AbstractBaseUser but instead using
    a OneToOneField relation with User
    '''

    class Meta:
        verbose_name = "User details"
        verbose_name_plural = "User details"

    user = models.OneToOneField(
        User,
        related_name='details',
        help_text='The django.contrib.auth User'
    )

    guest = models.BooleanField(
        default=False,
        help_text='Is this user a guest?'
    )

    builder = models.BooleanField(
        default=False,
        help_text='Is this user a package builder?'
    )

    tester = models.BooleanField(
        default=False,
        help_text='Is this user a tester of new features?'
    )

    def __unicode__(self):
        return 'UserDetails#%s(%s)' % (self.id, self.user.username)


def user_post_save(sender, user, created, **kwargs):
    '''
    Creates a UserDetails and a personal Account when a User is first created.
    '''
    from accounts.models import Account, AccountType
    if created:
        if not user.guest:
            account = Account.objects.create(
                name=user.username,
                type=AccountType.get('bronze'),
                personal=True
            )
            account.owners.add(user)

        UserDetails.objects.create(
            user=user
        )

models.signals.post_save.connect(
    user_post_save,
    sender=User,
    dispatch_uid="user_post_save"
)


def login_guest_user(request):
    '''
    Creates a guest user
    '''
    user = authenticate(stencila_guest_auth=True)
    login(request, user)


# Monkey patching of django.contrib.auth.models to
# allow for consistent usage of `serialize()` interface in
# API related views

def user_serialize(self, user, details=0):
    data = {
        'username': self.username,
        'url': 'https://stenci.la/users/%s' % self.username,
    }
    if details > 0:
        data['date_joined'] = self.date_joined
        if user == self:
            data['last_login'] = self.last_login
    return data

User.serialize = user_serialize


def anon_user_serialize(self, user):
    return {
        "username": None
    }

AnonymousUser.serialize = anon_user_serialize


class UserToken(models.Model):
    '''
    User tokens are used to authenticate without providing username/password pairs
    '''

    version = models.CharField(
        max_length=2,
        default="01",
        help_text="Version identifier for the token"
    )

    user = models.ForeignKey(
        User,
        related_name='tokens',
        help_text="The user this token represents"
    )

    origin = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="Origin that this token is valid for"
    )

    string = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="The actual token string"
    )

    name = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="Name for this token"
    )

    issued = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time that the token was created"
    )

    expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time that the token will expire"
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes about the token"
    )

    def save(self, *args, **kwargs):
        if self.user and not self.issued:
            self.issued = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            self.expires = self.issued + datetime.timedelta(days=365)
            self.string = self.encode()
        super(UserToken, self).save(*args, **kwargs)

    def serialize(self, user):
        assert user == self.user
        return OrderedDict([
            ('id', self.id),
            ('name', self.name),
            ('version', self.version),
            ('string', self.string),
            ('issued', self.issued),
            ('expires', self.expires),
            ('notes', self.notes)
        ])

    def encode(self):
        '''
        Encode a token string.

        Currently, the token is an combination of:

            <version> + base64(<salt> + encrypt(
                <token-password>,
                <token-secret> + ":" + <expiry-datetime> + ":" + <user-id>,
                <salt>
            ))

            * version : e.g. 01,02...ZZ; allows for us to change the token algorithm over time
            * token-password: used to encrypt the rest of the token
            * token-secret and expiry-datetime : embedded into the token so the database does not need to be touched
                to do first stage authentication to detect invalid, cracker generated tokens
            * user-id: for checking against what database says is user for this token
            * salt: required for encryption but also ensures each token is unique

        There are useful points about alternatives for token generation here:
            http://stackoverflow.com/questions/1626575/best-practices-around-generating-oauth-tokens
        '''
        if self.version == '01':
            expiry_as_secs = (self.expires - datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()
            plain = '%s:%i:%i' % (
                settings.USER_TOKEN_01_SECRET,
                expiry_as_secs,
                self.user.id
            )
            salt = Crypto.Random.new().read(16)
            encrypted = Crypto.Cipher.AES.new(
                settings.USER_TOKEN_01_PASSWORD,
                Crypto.Cipher.AES.MODE_CFB,
                salt
            ).encrypt(plain)
            return self.version + base64.b64encode(salt + encrypted)
        else:
            raise Exception('Invalid UserToken version:'+self.version)

    @staticmethod
    def decode(string):
        '''
        Decode a token string
        '''
        if len(string) >= 2:
            version = string[:2]
            if version == '01':
                unencoded = base64.b64decode(string[2:])
                salt = unencoded[:16]
                encrypted = unencoded[16:]
                plain = Crypto.Cipher.AES.new(
                    settings.USER_TOKEN_01_PASSWORD,
                    Crypto.Cipher.AES.MODE_CFB,
                    salt
                ).decrypt(encrypted)
                parts = plain.split(':')
                if len(parts) == 3:
                    secret, expires, user = parts
                    if secret == settings.USER_TOKEN_01_SECRET:
                        expires = int(expires)
                        if expires > time.time():
                            try:
                                user = int(user)
                            except TypeError:
                                Exception('Invalid UserToken user in token:'+string)
                            return string, version, expires, user
                        else:
                            raise Exception('Expired UserToken'+string)
                    else:
                        raise Exception('Invalid UserToken secret in token:'+string)
                else:
                    raise Exception('Invalid UserToken format in token:'+string)
            else:
                raise Exception('Invalid UserToken version:'+version)
        raise Exception('Token decoding failed')

    @staticmethod
    def authenticate(string):
        '''
        Authenticate a token string.
        Checks the token exists in the database (i.e. was at one time generated and has not been revoked).
        Returns the user associated with the token.
        Raise `PermissionDenied` errors for any failures
        '''
        # Attempt to decode the token
        try:
            string, version, expires, user = UserToken.decode(string)
        except:
            # Fail. Invalid
            raise PermissionDenied('Invalid user token')
        else:
            # Decoding succeeded, check the token exists in the database and has not expired
            try:
                # Check that token exists for the user
                token = UserToken.objects.get(user=user, string=string)
            except UserToken.DoesNotExist:
                # Fail. No such token
                raise PermissionDenied('Non-existent, or revoked, user token')
            else:
                # Check the token has not expired
                if token.expires > datetime.datetime.utcnow().replace(tzinfo=pytz.UTC):
                    return token.user
                else:
                    # Fail. Expired
                    raise PermissionDenied('Expired user token')
        return None

    @staticmethod
    def get_or_raise(**kwargs):
        '''
        Get a UserToken or raise an exception if it does not exist.
        '''
        try:
            return UserToken.objects.get(**kwargs)
        except UserToken.DoesNotExist:
            raise Http404()

    @staticmethod
    def get_sessions_token(user):
        '''
        Get the sessions token for the user
        '''
        token, created = UserToken.objects.get_or_create(
            user=user,
            name='Sessions token'
        )
        if created:
            token.notes = 'Token used by Stencila when launching sessions on your behalf'
            token.save()
        return token


class UserEvent(models.Model):
    '''
    User event recording and responses
    '''

    datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date/time the event occurred',
        auto_now_add=True
    )

    user = models.ForeignKey(
        User,
        related_name='events',
        help_text='The user this event is linked to'
    )

    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text='Name of the event'
    )

    data = jsonfield.JSONField(
        null=True,
        blank=True,
        help_text='Data associated with the event'
    )

    def __unicode__(self):
        return 'UserEvent(%s,%s)' % (self.id, self.name)

    @staticmethod
    def create(user, name, data):
        UserEvent.objects.create(
            user=user,
            name=name,
            data=data
        )
        if name == 'tester-request':
            if settings.MODE != 'local':
                mail_admins(
                    subject='tester-request: %s' % user.username,
                    message='tester-request: %s' % user.username
                )
