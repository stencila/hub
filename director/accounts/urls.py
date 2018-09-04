from django.urls import path

from accounts.views import AccountAccessView

urlpatterns = [
    path('<int:pk>/access', AccountAccessView.as_view(), name="account_access")
]
