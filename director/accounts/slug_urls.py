"""Implement the urlpatterns for the case when the URL starts with the account slug instead of /accounts/."""
from django.urls import path, include

import accounts.views as accounts_views
import accounts.subscription_views as subscription_views
import accounts.team_views as team_views

from lib.constants import AccountUrlRoot

urlpatterns = [
    path("", accounts_views.AccountProfileView.as_view(), name="account_profile"),
    path(
        AccountUrlRoot.members.value + "/",
        accounts_views.AccountAccessView.as_view(),
        name="account_access",
    ),
    path(
        AccountUrlRoot.settings.value + "/",
        accounts_views.AccountSettingsView.as_view(),
        name="account_settings",
    ),
    path(
        AccountUrlRoot.teams.value + "/create/",
        team_views.TeamDetailView.as_view(),
        name="account_team_create",
    ),
    path(
        AccountUrlRoot.teams.value + "/<int:team_pk>/",
        team_views.TeamDetailView.as_view(),
        name="account_team_detail",
    ),
    path(
        AccountUrlRoot.teams.value + "/<int:team_pk>/members/",
        team_views.TeamMembersView.as_view(),
        name="account_team_members",
    ),
    path(
        AccountUrlRoot.teams.value + "/<int:team_pk>/projects/",
        team_views.TeamProjectsView.as_view(),
        name="account_team_projects",
    ),
    path(
        AccountUrlRoot.teams.value + "/",
        team_views.TeamListView.as_view(),
        name="account_team_list",
    ),
    path(
        AccountUrlRoot.subscriptions.value + "/",
        subscription_views.SubscriptionListView.as_view(),
        name="account_subscriptions",
    ),
    path(
        AccountUrlRoot.subscriptions.value + "/add/",
        subscription_views.SubscriptionPlanListView.as_view(),
        name="account_subscriptions_plan_list",
    ),
    path(
        AccountUrlRoot.subscriptions.value + "/add/<int:plan_pk>/",
        subscription_views.AccountSubscriptionAddView.as_view(),
        name="account_subscriptions_add",
    ),
    path(
        AccountUrlRoot.subscriptions.value + "/<str:subscription_id>/",
        subscription_views.SubscriptionDetailView.as_view(),
        name="account_subscription_detail",
    ),
    path(
        AccountUrlRoot.subscriptions.value + "/<str:subscription_id>/cancel/",
        subscription_views.AccountSubscriptionCancelView.as_view(),
        name="account_subscription_cancel",
    ),
    path(
        AccountUrlRoot.subscription_signup.value + "/",
        subscription_views.SubscriptionSignupView.as_view(),
        name="account_subscription_signup",
    ),
    path("<slug:project_name>/", include("projects.slug_urls")),
]
