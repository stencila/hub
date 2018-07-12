"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from views import (
    HomeView,
    OpenView,
    UserSettingsView,
    UserSignupView,
    UserSigninView,
    UserSignoutView
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
    CheckoutLaunchView,
    CheckoutEventsView
)

urlpatterns = [

    path('projects/', include([
        path('',                  ProjectListView.as_view(),     name='project_list'),
        path('create/',           ProjectCreateView.as_view(),   name='project_create'),
        path('<int:pk>/',         ProjectReadView.as_view(),     name='project_read'),
        path('<int:pk>/update/',  ProjectUpdateView.as_view(),   name='project_update'),
        path('<int:pk>/delete/',  ProjectDeleteView.as_view(),   name='project_delete'),
        path('<int:pk>/archive/', ProjectArchiveView.as_view(),  name='project_archive')
    ])),

    path('checkouts/', include([
        path('',                  CheckoutListView.as_view(),     name='checkout_list'),
        path('create/',           CheckoutCreateView.as_view(),   name='checkout_create'),
        path('<int:pk>/',         CheckoutReadView.as_view(),     name='checkout_read'),
        path('<int:pk>/launch',   CheckoutLaunchView.as_view(),   name='checkout_launch'),
        path('<int:pk>/events',   CheckoutEventsView.as_view(),   name='checkout_events'),
    ])),

    path('me/',          UserSettingsView.as_view(), name='user_settings'),
    path('me/signup/',   UserSignupView.as_view(),   name='user_signup'),
    path('me/signin/',   UserSigninView.as_view(),   name='user_signin'),
    path('me/signout/',  UserSignoutView.as_view(),  name='user_signout'),
    path('me/',          include('allauth.urls')),

    path('open/',        OpenView.as_view(), name='open'),
    path('',             HomeView.as_view(), name='home'),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('debug/', include(debug_toolbar.urls)),
    ] + urlpatterns
