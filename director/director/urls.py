"""director URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
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
from django.contrib.auth.views import logout
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gallery', views.GalleryView.as_view(), name='gallery'),
    path('open/', views.OpenInput.as_view(), name='open'),
    path('open/<path:address>', views.OpenAddress.as_view(), name='open'),

    path('projects/<slug:user>/', views.ProjectListView.as_view(), name='list-projects'),

    path('project/new/', views.CreateProjectView.as_view(), name='create-project'),
    path('block/file-list/<slug:user>/<slug:project>/', views.StencilaProjectFilesBlock.as_view(), name='project-files-block'),
    path('files/<slug:user>/<slug:project>/', views.StencilaProjectDetailView.as_view(), name='project-files'),
    path('file/<slug:user>/<slug:project>/<path:filename>', views.StencilaProjectFileView.as_view(), name='project-file'),

    path('block/storer-projects/<slug:storer>/', views.StorerProjectBlock.as_view(), name='storer-project-block'),
    # User management (login, logout etc)
    # Mostly overrides of `allauth` views (often just to provide new templates).
    # The allauth URLs not overidden below are:
    #    password/change/                    account_change_password         change password
    #    password/set/                       account_set_password            confirmation that password is changed?
    #    inactive/                           account_inactive                notify user that account is inactive?
    #    email/                              account_email                   add, change and verify emails
    #    confirm-email/                      account_email_verification_sent
    #    confirm-email/(?P<key>\w+)/
    #    password/reset/                     account_reset_password
    #    password/reset/done/                account_reset_password_done
    #    password/reset/key/.../             account_reset_password_from_key
    #    password/reset/key/done/            account_reset_password_from_key_done
    #    social/login/cancelled/             socialaccount_login_cancelled
    #    social/login/error/                 socialaccount_login_error
    #    social/connections                  socialaccount_connections
    path('me/', views.UserSettingsView.as_view(), name='user_settings'),
    path('me/signup/', views.UserSignupView.as_view(), name='user_signup'),
    path('me/signin/', views.UserSigninView.as_view(), name='user_signin'),
    path('me/signout/', views.UserSignoutView.as_view(), name='user_signout'),
    path('me/join/', views.UserJoinView.as_view(), name='user_join'),
    path('me/', include('allauth.urls')),

    path('', views.FrontPageView.as_view(), name='home'),
]
