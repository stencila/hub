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

import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.utils import timezone

from general.api import API
from users.models import User
from invitations.models import Invitation

def accept(request, string):
    """
    @brief      View for accepting an invitation
    
    @param      request  The request
    @param      string   The string
    """
    api = API(request)

    # Get the invitation
    try:
        invitation = Invitation.objects.get(string=string)
    except Invitation.DoesNotExist:
        return api.raise_not_found()

    # If the invitatation has already expired, let the user know
    if invitation.sent + datetime.timedelta(days=invitation.expiry) < timezone.now():
        return render(request, 'invitations/expired.html', dict(
            invitation=invitation
        ))

    # Check whether the user need to be authenticated first
    if not request.user.is_authenticated():
        authed = False
    elif request.user.details.guest:
        # Logout the guest
        # TODO it would be better to "join up" the guest
        authed = False
    else:
        authed = True

    if authed:
        # Add the user to the key and redirect them to the path
        invitation.key.users.add(request.user)
        invitation.accepted = timezone.now()
        invitation.accepter = request.user
        invitation.save()
        return redirect(invitation.path)
    else:
        # Authenticate the user...
        if invitation.accepted:
            # Don't Offer the "express" login where we create
            # a new user if this invitation has already been accepted
            express_username = None
        else:
            # Create a username for "express" signin
            base = invitation.invitee.split('@')[0]
            express_username = base
            trials = 0
            while True:
                if User.objects.filter(username=express_username).count() == 0:
                    break
                trials += 1
                if trials > 1000000:
                    raise Exception("Maximum number of ")
                express_username = '%s%s' %(base, trials)

        # URL for redirect when using third party account
        # to login (come back to this view and get redirected)
        next = '/invitations/%s/accept' % string

        if api.get:
            # Render athentication forms
            return render(request, 'invitations/accept.html', dict(
                invitation=invitation,
                next=next,
                userpass_form=AuthenticationForm(),
                express_username=express_username
            ))
        elif api.post:
            if request.POST.get('userpass_signin'):
                # Attempt to signin with username/password
                form = AuthenticationForm(data=request.POST)
                if not form.is_valid():
                    # Display errors
                    return render(request, 'invitations/accept.html', dict(
                        invitation=invitation,
                        next=next,
                        userpass_form=form,
                        express_username=express_username
                    ))
                else:
                    # Login the user and then proceed with accept view
                    login(request, form.get_user())
                    # Continue recursively
                    return accept(request, string)
            elif express_username and request.POST.get('express_signin'):
                # Create a new user and log them in 
                user = User.objects.create_user(
                    username=express_username,
                    email=invitation.invitee
                )
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                # Continue recursively
                return accept(request, string)
            else:
                # Some thing else, just go back the page
                return redirect(next)
        else:
            return api.respond_bad()

