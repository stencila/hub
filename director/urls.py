from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from users.views import (
    UserSettingsView,
    UserSignupView,
    UserSigninView,
    UserSignoutView,
    BetaTokenView)

from checkouts.views import (
    CheckoutListView,
    CheckoutCreateView,
    CheckoutReadView,
    CheckoutOpenView,
    CheckoutSaveView,
    CheckoutCloseView)

import projects.urls

from views import HomeView

urlpatterns = [
    # Project CRUD
    path('projects/', include(projects.urls)),

    # Checkout CRUD
    path('checkouts/', include([
        path('', CheckoutListView.as_view(), name='checkout_list'),
        path('create/', CheckoutCreateView.as_view(), name='checkout_create'),
        path('<int:pk>/', CheckoutReadView.as_view(), name='checkout_read'),
        path('<int:pk>/open/', CheckoutOpenView.as_view(), name='checkout_open'),
        path('<int:pk>/save/', CheckoutSaveView.as_view(), name='checkout_save'),
        path('<int:pk>/close/', CheckoutCloseView.as_view(), name='checkout_close')
    ])),
    # Shortcut to `checkout_create`
    path('open/', CheckoutCreateView.as_view(), name='checkout_create_shortcut'),

    # User sign in, settings etc
    path('beta/', BetaTokenView.as_view(), name='user_beta'),
    path('me/', UserSettingsView.as_view(), name='user_settings'),
    path('me/signup/', UserSignupView.as_view(), name='user_signup'),
    path('me/signin/', UserSigninView.as_view(), name='user_signin'),
    path('me/signout/', UserSignoutView.as_view(), name='user_signout'),
    path('me/', include('allauth.urls')),

    # Staff admin
    path('admin/', admin.site.urls),

    # Home page
    path('', HomeView.as_view(), name='home'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('debug/', include(debug_toolbar.urls)),
                  ] + urlpatterns
