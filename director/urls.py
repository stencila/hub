from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from accounts.views import (
    AccountSettingsView,
    AccountSignupView,
    AccountSigninView,
    AccountSignoutView,
    BetaTokenView
)
from checkouts.views import (
    CheckoutListView,
    CheckoutCreateView,
    CheckoutReadView,
    CheckoutOpenView,
    CheckoutSaveView,
    CheckoutCloseView
)
from projects.session_parameters_views import SessionParametersListView, SessionParametersDetailView
from projects.views import (
    ProjectListView,
    ProjectReadView,
    ProjectDeleteView,
    ProjectArchiveView,

    ProjectDetailView, ProjectSessionsListView)
from projects.source_views import FilesSourceReadView, FilesSourceUpdateView, FilesSourceUploadView, \
    FilesProjectRemoveView, SourceListView, SourceDetailRouteView, SourceDetailView
from views import (
    HomeView
)

urlpatterns = [
    # Project CRUD
    path('projects/', include([
        # Generic views
        path('', ProjectListView.as_view(), name='project_list'),
        path('create/', ProjectDetailView.as_view(), name='project_create'),
        path('<int:pk>/', ProjectReadView.as_view(), name='project_read'),
        path('<int:pk>/update/', ProjectDetailView.as_view(), name='project_update'),
        path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
        path('<int:pk>/archive/', ProjectArchiveView.as_view(), name='project_archive'),
        path('<int:pk>/sessions/', ProjectSessionsListView.as_view(), name='project_sessions'),
        # Type-specific views
        path('files/<int:pk>/', FilesSourceReadView.as_view(), name='filesproject_read'),
        path('files/<int:pk>/update/', FilesSourceUpdateView.as_view(), name='filesproject_update'),
        path('files/<int:pk>/upload/', FilesSourceUploadView.as_view(), name='filesproject_upload'),
        path('files/<int:pk>/remove/<int:file>/', FilesProjectRemoveView.as_view(), name='filesproject_remove'),
    ])),

    path('session-parameters/', include([
        path('', SessionParametersListView.as_view(), name='sessionparameters_list'),
        path('create/', SessionParametersDetailView.as_view(), name='sessionparameters_create'),
        path('<int:pk>/', SessionParametersDetailView.as_view(), name='sessionparameters_update')
    ])),

    path('sources/', include([
        path('', SourceListView.as_view(), name='source_list'),
        path('create/', SourceDetailRouteView.as_view(), name='source_create_route'),
        path('<project_type>/create/', SourceDetailView.as_view(), name='source_create'),
        path('<project_type>/<int:pk>/', SourceDetailView.as_view(), name='source_detail'),
    ])),

    # Publisher views

    # path('publisher/', include([
    #     path('', PublisherMainView.as_view(), name='publisher_main'),
    #     path('session-groups/', SessionGroupListView.as_view(), name="session_group_list"),
    #     path('session-groups/create/', SessionGroupDetail.as_view(), name="session_group_create"),
    #     path('session-groups/<int:pk>/', SessionGroupDetail.as_view(), name="session_group_edit"),
    #     path('session-groups/<int:session_group_pk>/sessions/', SessionListView.as_view(), name="session_list"),
    #
    #     re_path(r'session-groups/(?P<token>[0-9a-f]+)/start-session', SessionStartView.as_view(),
    #             name="session_token_start"),
    #
    #     path('session-templates/', SessionTemplateListView.as_view(), name="session_template_list"),
    #     path('session-templates/create/', SessionTemplateDetailView.as_view(), name="session_template_create"),
    #     path('session-templates/<int:pk>/', SessionTemplateDetailView.as_view(), name="session_template_detail"),
    # ])),

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
    path('beta-token/', BetaTokenView.as_view(), name='beta_token'),
    path('me/', AccountSettingsView.as_view(), name='user_settings'),
    path('me/signup/', AccountSignupView.as_view(), name='user_signup'),
    path('me/signin/', AccountSigninView.as_view(), name='user_signin'),
    path('me/signout/', AccountSignoutView.as_view(), name='user_signout'),
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
