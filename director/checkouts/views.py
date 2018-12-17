import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView

from projects.permission_facade import fetch_project_for_user
from projects.permission_models import ProjectPermissionType
from .models import Checkout, CheckoutCreateError


class CheckoutListView(LoginRequiredMixin, ListView):
    model = Checkout
    paginate_by = 100


class CheckoutCreateView(LoginRequiredMixin, View):
    model = Checkout
    template_name = 'checkouts/checkout_create.html'

    def get(self, request):
        if 'project' in request.GET:
            project_fetch_result = fetch_project_for_user(request.user, request.GET['project'])

            if ProjectPermissionType.VIEW not in project_fetch_result.agent_permissions:
                raise PermissionDenied
            project = project_fetch_result.project
        else:
            project = None

        return render(request, self.template_name, {'project': project})

    def post(self, request):
        data = json.loads(request.body)
        project = data.get('project')
        try:
            checkout = Checkout.create(
                project=project,
                creator=request.user
            )
            return JsonResponse(checkout.json())
        except CheckoutCreateError as error:
            return JsonResponse({
                'error': error.serialize()
            })
        except Exception as error:
            return JsonResponse({
                'error': {
                    'message': str(error)
                }
            })


class CheckoutReadView(LoginRequiredMixin, View):
    model = Checkout
    template_name = 'checkouts/checkout_read.html'

    def get(self, request, pk):
        checkout = Checkout.obtain(pk=pk, user=request.user)
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            return JsonResponse(checkout.json())
        else:
            return render(request, self.template_name, checkout)


class CheckoutOpenView(LoginRequiredMixin, View):

    def post(self, request, pk):
        checkout = Checkout.obtain(pk=pk, user=request.user)
        checkout.open()
        return JsonResponse(checkout.json())


@method_decorator(csrf_exempt, name='dispatch')
class CheckoutSaveView(LoginRequiredMixin, View):

    def post(self, request, pk):
        checkout = Checkout.obtain(pk=pk, user=request.user)
        checkout.save_()
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class CheckoutCloseView(LoginRequiredMixin, View):

    def post(self, request, pk):
        checkout = Checkout.obtain(pk=pk, user=request.user)
        checkout.close()
        return HttpResponse()
