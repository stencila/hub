from django.urls import path

import checkouts.views

urlpatterns = [
    path('', checkouts.views.CheckoutListView.as_view(), name='checkout_list'),
    path('create/', checkouts.views.CheckoutCreateView.as_view(), name='checkout_create'),
    path('<int:pk>/', checkouts.views.CheckoutReadView.as_view(), name='checkout_read'),
    path('<int:pk>/open/', checkouts.views.CheckoutOpenView.as_view(), name='checkout_open'),
    path('<int:pk>/save/', checkouts.views.CheckoutSaveView.as_view(), name='checkout_save'),
    path('<int:pk>/close/', checkouts.views.CheckoutCloseView.as_view(), name='checkout_close')
]
