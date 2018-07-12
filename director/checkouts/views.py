from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView

from .models import Checkout, CheckoutEvent
from .forms import CheckoutCreateForm


class CheckoutListView(ListView):
    model = Checkout
    paginate_by = 100


class CheckoutCreateView(CreateView):
    model = Checkout
    form_class = CheckoutCreateForm
    template_name = 'checkouts/checkout_create.html'

    def get_success_url(self):
        return reverse('checkout_read', args=[self.object.id])


class CheckoutReadView(DetailView):
    model = Checkout
    fields = '__all__'
    template_name = 'checkouts/checkout_read.html'


class CheckoutLaunchView(View):
    """
    TODO: check this is only accessible to the creator of the checkout
    """

    def post(self, request, pk):
        checkout = Checkout.objects.get(
            id=pk
        )
        checkout.launch()
        return HttpResponse()


class CheckoutEventsView(View):

    def get(self, request, pk):
        since = request.GET.get('since', 0)
        events = CheckoutEvent.objects.filter(
            checkout=pk,
            id__gt=since
        ).values()
        return JsonResponse(
            list(events),
            content_type='application/json',
            safe=False
        )
