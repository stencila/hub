from django.urls import path, include

import users.views

urlpatterns = [
    path('', users.views.UserSettingsView.as_view(), name='user_settings'),
    path('signup/', users.views.UserSignupView.as_view(), name='user_signup'),
    path('signin/', users.views.UserSigninView.as_view(), name='user_signin'),
    path('signout/', users.views.UserSignoutView.as_view(), name='user_signout'),
    path('username/', users.views.UsernameChangeView.as_view(), name='user_change_username'),
    path('avatar/', include('avatar.urls')),
    path('', include('allauth.urls')),
]
