import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import View, DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView

from .models import Checkout


class CheckoutListView(LoginRequiredMixin, ListView):
    model = Checkout
    paginate_by = 100


class CheckoutCreateView(LoginRequiredMixin, View):
    model = Checkout
    template_name = 'checkouts/checkout_create.html'

    def get(self, request):
        """
        Render the form
        """
        return render(request, self.template_name)

    def post(self, request):
        """
        Create the checkout from the submitted form
        """
        data = json.loads(request.body)
        project = data.get('project')
        try:
            checkout = Checkout.create(project)
            return JsonResponse(checkout.json())
        except Exception as error:
            return JsonResponse({
                'error': str(error)
            })


class CheckoutReadView(LoginRequiredMixin, View):
    """
    A static view for reading a checkout, usually an
    inactive one and accessing it's events, downloading
    associated files etc
    """
    model = Checkout
    template_name = 'checkouts/checkout_read.html'

    def get(self, request, pk):
        """
        """
        checkout = Checkout.obtain(pk=pk, user=request.user)
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            return JsonResponse(checkout.json())
        else:
            return render(request, self.template_name, checkout)


class CheckoutLaunchView(LoginRequiredMixin, View):

    def post(self, request, pk):
        checkout = Checkout.obtain(pk=pk, user=request.user)
        checkout.launch()
        return JsonResponse(checkout.json())
