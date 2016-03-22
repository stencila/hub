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

import os
import urllib
import hashlib
from collections import OrderedDict

from PIL import Image, ImageFont, ImageDraw

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from components.models import Address
from general.errors import Error


class AccountType(models.Model):

    name = models.CharField(
        max_length=24,
        unique=True,
        help_text='The name of this account type.'
    )

    @staticmethod
    def get(name):
        '''
        Return an account creating it if it does no exist
        '''
        assert name in ('bronze', 'silver', 'gold', 'platinum')
        account, created = AccountType.objects.get_or_create(
            name=name
        )
        return account

    def __unicode__(self):
        return 'AccountType#%s(%s)' % (self.id, self.name)


def account_logo_path(instance, filename):
    '''
    Creates a filename path for an Account logo

    Use the generic name 'logo' for privacy reasons.
    Need to append the right extension to the end.
    '''
    root, extension = os.path.splitext(filename)
    # Note that path is relative to MEDIA_ROOT!
    return os.path.join('accounts', str(instance.id), 'logo%s' % extension)

# Pre load font used for fallback account logos
account_logo_font = ImageFont.truetype(os.path.join(
    settings.BASE_DIR, "general/static/fonts/Inconsolata-Bold.ttf"
), 200)


class Account(models.Model):

    name = models.CharField(
        max_length=256,
        null=False,
        unique=True,
        help_text='Name of this account'
    )

    type = models.ForeignKey(
        AccountType,
        related_name='accounts',
        help_text='Type of this account',
    )

    personal = models.BooleanField(
        default=False,
        help_text='Is this a personal account?'
    )

    owners = models.ManyToManyField(
        User,
        related_name='accounts',
        help_text='The owners of this account'
    )

    logo = models.ImageField(
        null=True,
        blank=True,
        upload_to=account_logo_path,
        max_length=1024,
        help_text='Logo of account'
    )

    gravatar_email = models.EmailField(
        null=True,
        blank=True,
        max_length=254,  # Max. length of RFC3696/5321-compliant email addresses
        help_text='The email address used to retreive the account logo from gravatar.com'
    )

    hue = models.IntegerField(
        null=True,
        blank=True,
        help_text='Color hue used for this account.'
                  'Degrees of color wheel: around 0 and 360 are reds, 120 greens, 240 blues.'
    )

    def __unicode__(self):
        return 'Account#%s(%s)' % (self.id, self.name)

    def serialize(self, request):
        return OrderedDict([
            ('name', self.name),
            ('logo', self.logo_url()),
            ('hue', self.hue),
        ])

    def save(self, *args, **kwargs):
        '''
        Override `save()` to ensure associated models have been
        created
        '''
        # Do save first to get an id
        super(Account, self).save(*args, **kwargs)
        # Ensure an address is present for this account
        if self.addresses.filter(id=self.name).count() == 0:
            Address.objects.create(
                id=self.name,
                account=self
            )

    def logo_url(self, size=64, absolute=False):
        '''
        Returns a URL for this account's logo.

        Tries the generate logo using the alternatives:
            - `logo` ImageField
            - `gravatar_email` EmailField
            - generatated logo
        '''
        if self.logo:
            # Use the accounts's uploaded logo
            return self.logo.url
        elif self.gravatar_email:
            # Generate gravatar.com URL
            url = "https://www.gravatar.com/avatar/"
            # Add hashed email. See https://en.gravatar.com/site/implement/hash/
            url += hashlib.md5(self.gravatar_email.lower()).hexdigest()
            # Add options. See https://en.gravatar.com/site/implement/images/
            url += "?" + urllib.urlencode({
                'd': 'retro',
                's': size
            })
            return url
        else:
            # Generate a logo and return its URL
            path = 'dynamic/accounts/%i/logo.png' % self.id
            filename = os.path.join(settings.BASE_DIR, path)
            if not os.path.exists(filename):
                dirname = os.path.dirname(filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                letters = self.name[:2]
                logo = Image.new("RGBA", (250, 250), (0, 173, 238))
                draw = ImageDraw.Draw(logo)
                draw.text((25, 5), letters, fill=(255, 255, 255), font=account_logo_font)
                logo.save(filename)
            if absolute:
                return 'https://stenci.la/'+path
            else:
                return path

    def address_add(self, id, public=False):
        '''
        Add an address for this account
        '''
        Address.objects.create(
            id=id,
            public=public,
            account=self
        )

    def sufficient(self, type, public=False, quantity=1):
        '''
        Does the account have sufficient resource credit to use
        additional <quantity> of <type>
        '''
        if public:
            return True
        if self.type.name == 'platinum':
            return True
        else:
            return False

    def sufficient_or_raise(self, type, public=False, quantity=1):
        '''
        Check there are enough resource credits or else raise
        an `InsufficientResourcesError`
        '''
        if not self.sufficient(type, quantity):
            raise Account.InsufficientResourcesError(self, type, quantity)
        else:
            return True

    ##########################################################################
    # Errors

    class NonexistantError(Error):
        code = 404

        def __init__(self, name):
            self.name = name

        def serialize(self):
            return dict(
                error='account:nonexistant',
                message='No account with this name exists.',
                url='https://stenci.la/api/errors/account/nonexistent',
                name=self.name
            )

    class InsufficientResourcesError(Error):
        code = 400

        def __init__(self, account, type, public, quantity):
            self.account = account
            self.type = type
            self.public = public
            self.quantity = quantity

        def serialize(self):
            return dict(
                error='account:insufficient-resources',
                message='Requested resources exceed those available for the account',
                url='https://stenci.la/api/errors/account/insufficient-resources',
                account=dict(
                    name=self.account.name,
                    id=self.account.id,
                    type=self.account.type.name
                ),
                type=self.type,
                public=self.public,
                quantity=self.quantity
            )
