from django.urls import path

from accounts.views import (
    AccountListView, AccountProfileView, AccountAccessView, AccountSettingsView, AccountCreateView)
from accounts.subscription_views import SubscriptionListView, SubscriptionPlanListView, \
    AccountSubscriptionAddView, SubscriptionSignupView, SubscriptionDetailView, AccountSubscriptionCancelView
from accounts.team_views import TeamDetailView, TeamListView, TeamMembersView, TeamProjectsView

urlpatterns = [
    path('', AccountListView.as_view(), name='account_list'),
    path('create', AccountCreateView.as_view(), name='account_create'),
    path('<int:pk>/', AccountProfileView.as_view(), name='account_profile'),
    path('<int:pk>/members/', AccountAccessView.as_view(), name='account_access'),
    path('<int:pk>/settings/', AccountSettingsView.as_view(), name='account_settings'),
    path('create/', AccountCreateView.as_view(), name='accounts_create'),
    path('<int:account_pk>/teams/create', TeamDetailView.as_view(), name='account_team_create'),
    path('<int:account_pk>/teams/<int:team_pk>', TeamDetailView.as_view(), name='account_team_detail'),
    path('<int:account_pk>/teams/<int:team_pk>/members', TeamMembersView.as_view(), name='account_team_members'),
    path('<int:account_pk>/teams/<int:team_pk>/projects', TeamProjectsView.as_view(), name='account_team_projects'),
    path('<int:account_pk>/teams', TeamListView.as_view(), name='account_team_list'),

    path('<int:pk>/subscriptions/', SubscriptionListView.as_view(), name='account_subscriptions'),
    path('<int:pk>/subscriptions/add', SubscriptionPlanListView.as_view(),
         name='account_subscriptions_plan_list'),
    path('<int:pk>/subscriptions/<str:subscription_id>', SubscriptionDetailView.as_view(),
         name='account_subscription_detail'),
    path('<int:pk>/subscriptions/<str:subscription_id>/cancel', AccountSubscriptionCancelView.as_view(),
         name='account_subscription_cancel'),
    path('<int:pk>/customer-create/', SubscriptionSignupView.as_view(),
         name='account_subscription_customer_create'),
    path('<int:pk>/subscriptions/add/<int:plan_pk>/', AccountSubscriptionAddView.as_view(),
         name='account_subscriptions_add'),

]
