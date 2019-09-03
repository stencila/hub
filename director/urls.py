from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.defaults import permission_denied, page_not_found

import projects.urls
from accounts.urls import urlpatterns as accounts_patterns
from open.urls import urlpatterns as open_patterns
from api_urls import urlpatterns as api_patterns
from stencila_admin.urls import urlpatterns as stencila_admin_patterns
from checkouts.views import (
    CheckoutListView,
    CheckoutCreateView,
    CheckoutReadView,
    CheckoutOpenView,
    CheckoutSaveView,
    CheckoutCloseView)
from users.views import (
    UsernameChangeView,
    UserSettingsView,
    UserSignupView,
    UserSigninView,
    UserSignoutView,
    BetaTokenView)
from views import (
    AboutView,
    ContactView,
    HelpView,
    HomeView,
    IcoView,
    Test403View,
    Test404View,
    Test500View,
    PrivacyView,
    StatusView,
    TermsView, IeUnsupportedView, error_500_view)

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
    path('checkout/', CheckoutCreateView.as_view(), name='checkout_create_shortcut'),

    # User sign in, settings etc
    path('beta/', BetaTokenView.as_view(), name='user_beta'),
    path('me/', UserSettingsView.as_view(), name='user_settings'),
    path('me/signup/', UserSignupView.as_view(), name='user_signup'),
    path('me/signin/', UserSigninView.as_view(), name='user_signin'),
    path('me/signout/', UserSignoutView.as_view(), name='user_signout'),
    path('me/username/', UsernameChangeView.as_view(), name='user_change_username'),
    path('me/avatar/', include('avatar.urls')),
    path('me/', include('allauth.urls')),

    # Staff admin
    path('admin/', admin.site.urls),

    # Home page
    path('', HomeView.as_view(), name='home'),

    # About pages etc
    path('about/', AboutView.as_view(), name='about'),
    path('about/contact/', ContactView.as_view(), name='contact'),
    path('about/help/', HelpView.as_view(), name='help'),
    path('about/privacy-policy/', PrivacyView.as_view(), name='privacy-policy'),
    path('about/terms-and-conditions/', TermsView.as_view(), name='terms-and-conditions'),

    # Accounts App
    path('accounts/', include(accounts_patterns)),

    # Open App
    path('open/', include(open_patterns)),

    # Stencila Admin App (not Django Admin)
    path('stencila-admin/', include(stencila_admin_patterns)),

    # API
    path('api/', include(api_patterns)),

    path('ie-unsupported/', IeUnsupportedView.as_view(), name='ie-unsupported'),

    # Testing errors
    path('test/403', Test403View.as_view()),
    path('test/404', Test404View.as_view()),
    path('test/500', Test500View.as_view()),

    # status
    path('system-status/', StatusView.as_view()),

    # ico for old browsers
    path('favicon.ico', IcoView.as_view())
]

handler403 = permission_denied
handler404 = page_not_found
handler500 = error_500_view

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('debug/', include(debug_toolbar.urls)),
    ] + urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
