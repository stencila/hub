"""Implement the urlpatterns for the case when the URL starts with the account slug instead of /accounts/."""
from django.urls import path, include

import accounts.views as accounts_views
import accounts.subscription_views as subscription_views
import accounts.team_views as team_views

from lib.constants import AccountUrlRoot

urlpatterns = [
    path('', accounts_views.AccountProfileView.as_view(), name='account_profile_slug'),
    path(AccountUrlRoot.members.value + '/', accounts_views.AccountAccessView.as_view(), name='account_access_slug'),
    path(AccountUrlRoot.settings.value + '/', accounts_views.AccountSettingsView.as_view(),
         name='account_settings_slug'),

    path(AccountUrlRoot.teams.value + '/create/', team_views.TeamDetailView.as_view(),
         name='account_team_create_slug'),
    path(AccountUrlRoot.teams.value + '/<int:team_pk>/', team_views.TeamDetailView.as_view(),
         name='account_team_detail_slug'),
    path(AccountUrlRoot.teams.value + '/<int:team_pk>/members/', team_views.TeamMembersView.as_view(),
         name='account_team_members_slug'),
    path(AccountUrlRoot.teams.value + '/<int:team_pk>/projects/', team_views.TeamProjectsView.as_view(),
         name='account_team_projects_slug'),
    path(AccountUrlRoot.teams.value + '/', team_views.TeamListView.as_view(),
         name='account_team_list_slug'),

    path(AccountUrlRoot.subscriptions.value + '/', subscription_views.SubscriptionListView.as_view(),
         name='account_subscriptions_slug'),
    path(AccountUrlRoot.subscriptions.value + '/add/', subscription_views.SubscriptionPlanListView.as_view(),
         name='account_subscriptions_plan_list_slug'),
    path(AccountUrlRoot.subscriptions.value + '/add/<int:plan_pk>/',
         subscription_views.AccountSubscriptionAddView.as_view(), name='account_subscriptions_add_slug'),
    path(AccountUrlRoot.subscriptions.value + '/<str:subscription_id>/',
         subscription_views.SubscriptionDetailView.as_view(), name='account_subscription_detail_slug'),
    path(AccountUrlRoot.subscriptions.value + '/<str:subscription_id>/cancel/',
         subscription_views.AccountSubscriptionCancelView.as_view(),
         name='account_subscription_cancel_slug'),
    path(AccountUrlRoot.subscription_signup.value + '/', subscription_views.SubscriptionSignupView.as_view(),
         name='account_subscription_signup_slug'),
    path('<slug:project_slug>/', include('projects.slug_urls'))
]
