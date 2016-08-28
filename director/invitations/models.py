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
import datetime

from django.db import models
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings

from users.models import User
from components.models import Key


def invitation_create_string():
    return get_random_string(64,'abcdefghijklmnopqrstuvwxyz0123456789')

class Invitation(models.Model):
    '''
    Invitations are for providing access to people who may not have a Stencila account.

    An invitation is sent to the `invitee` (for now via email) who clicks on the link, is 
    asked to either signin or to create an account and is then redirected to the component URL.

    We should ensure that only users with AUTHORIZE rights on a component gets to send an invitation.

    We should warn users if they are sneding an invitation to a an email addres that is not
    associated with a current user.
    For example, Google Drive tells you : "You are sending an invitation to example@example.com. 
    Since there is no Google account associated with this email address, anyone holding this 
    invitation will have access without signing in."
    '''

    inviter = models.ForeignKey(
        User,
        help_text='User giving the invitation',
        related_name='invitations_given'
    )

    invitee = models.CharField(
        max_length=255,
        null=False,
        help_text='An identifier for the person receiving the invitation. Usually an email address'
    )

    platform_choices = [
        ('email', 'Email')
    ]

    platform = models.CharField(
        max_length=16,
        default='email',
        choices=platform_choices,
        help_text='The platform for sending the invitation.'
    )

    subject = models.CharField(
        max_length=255,
        help_text='The subject of the invitation',
    )

    message = models.TextField(
        help_text='The message of the invitation',
    )

    path = models.CharField(
        null=False,
        max_length=255,
        help_text='The path to redirect the intivtee to after acceptance',
    )

    key = models.ForeignKey(
        Key,
        related_name='invitation_keys',
        help_text='The access key to be given to the invitee',
    )

    string = models.CharField(
        max_length=64,
        default=invitation_create_string,
        unique=True,
        help_text='A string of character used to identify this invitation',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        help_text='Time that this invitation was created'
    )

    sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this invitation was sent to invitee'
    )

    expiry = models.FloatField(
        default=7,
        help_text='Number of days until this invitation expires. Can be fractional e.g. 0.2'
    )

    accepted = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time that this invitation was accepted by the invitee'
    )

    accepter = models.ForeignKey(
        User,
        null=True,
        help_text='User who accepted the invitation',
        related_name='invitations_accepted'
    )

    def __unicode__(self):
        return 'Invitation#%s(%s)' % (self.id, self.invitee)

    def accept_url(self):
        return '/invitations/%s/accept' % self.string

    def send(self):
        if self.platform == 'email':
            self.send_email()
        else:
            raise Exception('Unhandled platform: ' + self.platform)

        self.sent = timezone.now()
        self.save()

    def send_email(self):
        subject = self.subject
        body = render_to_string(
            'invitations/email/body.html',
            dict(
                inviter=self.inviter,
                type='document',
                action='edit',
                message=self.message,
                accept_url=self.accept_url(),
                expiry=self.expiry
            )
        )
        email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [self.invitee]
        )
        email.content_subtype = 'html'
        email.send()
