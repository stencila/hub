from django.urls import path

from accounts.views import (AccountListView, AccountCreateView, AccountNameRedirectView)
from lib.constants import AccountUrlRoot

urlpatterns = [
    path('', AccountListView.as_view(), name='account_list'),
    path(AccountUrlRoot.create.value + '/', AccountCreateView.as_view(), name='account_create'),

    path('<int:pk>/', AccountNameRedirectView.as_view(), name='account_redirect'),
    path('<int:pk>/<path:path>', AccountNameRedirectView.as_view(), name='account_redirect_path')
]
