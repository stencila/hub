from django.urls import path

from accounts.views import (
    AccountListView, AccountProfileView, AccountAccessView, AccountSettingsView, AccountCreateView)
from accounts.subscription_views import SubscriptionListView, SubscriptionPlanListView, \
    AccountSubscriptionAddView, SubscriptionSignupView, SubscriptionDetailView, AccountSubscriptionCancelView
from accounts.team_views import TeamDetailView, TeamListView, TeamMembersView, TeamProjectsView
from lib.constants import AccountUrlRoot

urlpatterns = [
    path('', AccountListView.as_view(), name='account_list'),
    path(AccountUrlRoot.create.value + '/', AccountCreateView.as_view(), name='account_create'),

    path('<int:pk>/', AccountProfileView.as_view(), name='account_profile'),
    path('<int:pk>/' + AccountUrlRoot.members.value + '/', AccountAccessView.as_view(), name='account_access'),
    path('<int:pk>/' + AccountUrlRoot.settings.value + '/', AccountSettingsView.as_view(), name='account_settings'),

    path('<int:account_pk>/' + AccountUrlRoot.teams.value + '/create/', TeamDetailView.as_view(),
         name='account_team_create'),
    path('<int:account_pk>/' + AccountUrlRoot.teams.value + '/<int:team_pk>/', TeamDetailView.as_view(),
         name='account_team_detail'),
    path('<int:account_pk>/' + AccountUrlRoot.teams.value + '/<int:team_pk>/members/', TeamMembersView.as_view(),
         name='account_team_members'),
    path('<int:account_pk>/' + AccountUrlRoot.teams.value + '/<int:team_pk>/projects/', TeamProjectsView.as_view(),
         name='account_team_projects'),
    path('<int:account_pk>/' + AccountUrlRoot.teams.value + '/', TeamListView.as_view(), name='account_team_list'),

    path('<int:pk>/' + AccountUrlRoot.subscriptions.value + '/add/<int:plan_pk>/', AccountSubscriptionAddView.as_view(),
         name='account_subscriptions_add'),
    path('<int:pk>/' + AccountUrlRoot.subscriptions.value + '/', SubscriptionListView.as_view(),
         name='account_subscriptions'),
    path('<int:pk>/' + AccountUrlRoot.subscriptions.value + '/add/', SubscriptionPlanListView.as_view(),
         name='account_subscriptions_plan_list'),
    path('<int:pk>/' + AccountUrlRoot.subscriptions.value + '/<str:subscription_id>/', SubscriptionDetailView.as_view(),
         name='account_subscription_detail'),
    path('<int:pk>/' + AccountUrlRoot.subscriptions.value + '/<str:subscription_id>/cancel/',
         AccountSubscriptionCancelView.as_view(),
         name='account_subscription_cancel'),
    path('<int:pk>/' + AccountUrlRoot.subscription_signup.value + '/', SubscriptionSignupView.as_view(),
         name='account_subscription_signup')
]
