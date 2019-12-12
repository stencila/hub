import json
import typing

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from djstripe import settings as djstripe_settings
from djstripe.models import Product, Plan, Customer, PaymentMethod, Subscription

from accounts.models import AccountPermissionType, AccountSubscription
from accounts.static_product_config import FREE_PRODUCT, FREE_PLAN
from accounts.views import AccountPermissionsMixin
from lib.resource_allowance import account_resource_allowance


class ProductPlan(typing.NamedTuple):
    """
    Pull out the import parts of Product and Plan + add info about if the user has a subscription.

    For easier use in templates.
    """

    product: typing.Union[Product, dict]
    plan: typing.Union[Plan, dict]
    is_subscribed: bool


class SubscriptionPlanListView(AccountPermissionsMixin, View):
    """Display a list of Plans to which the Account can be subscribed."""

    required_account_permission = AccountPermissionType.ADMINISTER

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.request_permissions_guard(request, pk)
        # Plans are retrieved from Products. We assume 1 Plan per Product although there technically could be more
        products = Product.objects.all()

        subscription_plans = [
            account_subscription.subscription.plan for account_subscription in self.account.subscriptions.all()
            if account_subscription.subscription.is_status_current()
        ]

        product_plans = [
            ProductPlan(FREE_PRODUCT, FREE_PLAN, len(subscription_plans) == 0)
        ]

        for product in products:
            plan = product.plan_set.first()
            product_plans.append(ProductPlan(product, plan, plan in subscription_plans))

        return render(request, 'accounts/plan_list.html', self.get_render_context({
            'product_plans': product_plans
        }))


class SubscriptionListView(AccountPermissionsMixin, View):
    """List all the Subscriptions for the Account."""

    required_account_permission = AccountPermissionType.ADMINISTER

    def get(self, request: HttpRequest, pk: int) -> HttpRequest:
        self.request_permissions_guard(request, pk)

        account_resource_allowance(self.account)

        account_subscriptions = AccountSubscription.objects.filter(account=self.account).order_by(
            '-subscription__current_period_start')

        return render(request, 'accounts/account_subscriptions.html', self.get_render_context({
            'account_subscriptions': account_subscriptions
        }))


class SubscriptionDetailView(AccountPermissionsMixin, View):
    """Show the details of a particular Subscription."""

    required_account_permission = AccountPermissionType.ADMINISTER

    def get(self, request: HttpRequest, pk: int, subscription_id: str) -> HttpResponse:
        self.request_permissions_guard(request, pk)
        subscription = Subscription.objects.get(id=subscription_id)

        return render(request, 'accounts/account_subscription.html', self.get_render_context({
            'subscription': subscription
        }))


class AccountSubscriptionCancelView(AccountPermissionsMixin, View):
    required_account_permission = AccountPermissionType.ADMINISTER

    def post(self, request: HttpRequest, pk: int, subscription_id: str) -> HttpResponse:
        self.request_permissions_guard(request, pk)
        subscription = Subscription.objects.get(id=subscription_id)

        product_name = subscription.plan.product.name

        cancel_at_period_end = request.POST.get('cancel_at', 'period_end') == 'period_end'

        subscription.cancel(cancel_at_period_end)

        if cancel_at_period_end:
            cancel_message = 'Your {} subscription will be cancelled at the end of its current period.'.format(
                product_name)
        else:
            cancel_message = 'Your {} subscription was cancelled.'.format(product_name)

        messages.success(request, cancel_message)

        return redirect('account_subscriptions', pk)


class AccountSubscriptionAddView(AccountPermissionsMixin, View):
    """
    Display form for getting the User email address and credit card details.

    Subscriptions signup is done with a JS request to SubscriptionSignupView
    """

    required_account_permission = AccountPermissionType.ADMINISTER

    def get(self, request: HttpRequest, pk: int, plan_pk: int) -> HttpResponse:
        self.request_permissions_guard(request, pk)
        plan = get_object_or_404(Plan, pk=plan_pk)

        verified_emails = request.user.emailaddress_set.filter(verified=True).order_by('email')

        if verified_emails.count() == 0:
            messages.error(request, 'You can not sign up for a new subscription as you do not have a verified email '
                                    'address, please add or verify an email address then return to the subscriptions '
                                    'page.')
            return redirect('account_email')

        # TODO: If no verified emails, redirect to the email setup page

        context = {'plan': plan, 'STRIPE_PUBLIC_KEY': djstripe_settings.STRIPE_PUBLIC_KEY, 'emails': verified_emails}

        return render(request, 'accounts/subscription_add.html', self.get_render_context(context))


class SubscriptionSignupView(AccountPermissionsMixin, View):
    """Create or get the Customer, then subscribe them to a plan."""

    required_account_permission = AccountPermissionType.ADMINISTER

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.request_permissions_guard(request, pk)

        data = json.loads(request.body)

        customer_id = data.get('customer_id')

        if not customer_id:
            email = request.user.emailaddress_set.filter(email=data['email'], verified=True).first()

            if not email:
                raise ValueError('Validated email address {} was not found for the customer.'.format(email.email))

            dj_customer, created = Customer.get_or_create(subscriber=request.user)

            PaymentMethod.attach(data['payment_method'], dj_customer)

            customer = dj_customer.api_retrieve()

            customer['invoice_settings'] = {'default_payment_method': data['payment_method']}
            customer.save()

            dj_customer.sync_from_stripe_data(customer)
        else:
            try:
                dj_customer = Customer.objects.get(djstripe_id=customer_id)
            except Customer.DoesNotExist:
                raise ValueError("TODO: Raise better error for missing Customer.")

            if dj_customer.subscriber != request.user:
                raise PermissionDenied('The current user does not own this Customer.')

        try:
            plan = Plan.objects.get(id=data['plan'])
        except Plan.DoesNotExist:
            raise ValueError("TODO: Raise better error for missing Plan")

        subscription = dj_customer.subscribe(plan)

        AccountSubscription.objects.create(account=self.account, subscription=subscription)

        messages.success(request, 'Sign up to {} subscription was successful.'.format(plan.name))

        return JsonResponse({'success': True, 'customer_id': dj_customer.djstripe_id,
                             'redirect': reverse('account_subscription_detail',
                                                 args=(self.account.pk, subscription.id))})
