from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from accounts.views import (
    AccountSettingsView,
    AccountSignupView,
    AccountSigninView,
    AccountSignoutView
)
from projects.views import (
    ProjectListView,
    ProjectCreateView,
    ProjectReadView,
    ProjectUpdateView,
    ProjectDeleteView,
    ProjectArchiveView
)
from checkouts.views import (
    CheckoutListView,
    CheckoutCreateView,
    CheckoutReadView,
    CheckoutOpenView,
    CheckoutSaveView
)

urlpatterns = [
    # Project CRUD
    path('projects/', include([
        path('',                  ProjectListView.as_view(),      name='project_list'),
        path('create/',           ProjectCreateView.as_view(),    name='project_create'),
        path('<int:pk>/',         ProjectReadView.as_view(),      name='project_read'),
        path('<int:pk>/update/',  ProjectUpdateView.as_view(),    name='project_update'),
        path('<int:pk>/delete/',  ProjectDeleteView.as_view(),    name='project_delete'),
        path('<int:pk>/archive/', ProjectArchiveView.as_view(),   name='project_archive')
    ])),
    # Home is shortcut to `project_list`
    path('',                      ProjectListView.as_view(),      name='home'),

    # Checkout CRUD
    path('checkouts/', include([
        path('',                  CheckoutListView.as_view(),     name='checkout_list'),
        path('create/',           CheckoutCreateView.as_view(),   name='checkout_create'),
        path('<int:pk>/',         CheckoutReadView.as_view(),     name='checkout_read'),
        path('<int:pk>/open/',    CheckoutOpenView.as_view(),     name='checkout_open'),
        path('<int:pk>/save/',    CheckoutSaveView.as_view(),     name='checkout_save')
    ])),
    # Shortcut to `checkout_create`
    path('open/',                 CheckoutCreateView.as_view(),   name='checkout_create_shortcut'),

    # User sign in, settings etc
    path('me/',                   AccountSettingsView.as_view(),  name='user_settings'),
    path('me/signup/',            AccountSignupView.as_view(),    name='user_signup'),
    path('me/signin/',            AccountSigninView.as_view(),    name='user_signin'),
    path('me/signout/',           AccountSignoutView.as_view(),   name='user_signout'),
    path('me/',                   include('allauth.urls')),

    # Staff admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('debug/', include(debug_toolbar.urls)),
    ] + urlpatterns
