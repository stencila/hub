"""
Custom webhooks to add behavior when subscriptions change.

Note that the `djstripe` webhooks already do the syncing of data (ie. Stripe
to database).

To test these webhooks see the docs (https://stripe.com/docs/webhooks/test) e.g.

    stripe listen --forward-to localhost:8000/stencila/stripe/webhook/

Then set the webhook signing secret displayed as an environment variable

    DJANGO_DJSTRIPE_WEBHOOK_SECRET=whsec_r3lKX3vJgqmgLrJNLtVpDpPdIsoIm2Ew  make run
"""

from djstripe import webhooks
from djstripe.models import Customer, Subscription


@webhooks.handler("customer.updated")
def customer_updated(event, **kwargs):
    """
    When customer updates billing information on Stripe, transfer to account fields.
    """
    from accounts.models import AccountTier

    customer = Customer.objects.get(id=event.data["object"]["id"])

    account = customer.account
    account.billing_email = customer.email
    account.save()


@webhooks.handler("customer.subscription.updated")
def subscription_updated(event, **kwargs):
    """
    When the subscription is updated, change the account's tier.
    """
    from accounts.models import AccountTier

    subscription = Subscription.objects.get(id=event.data["object"]["id"])

    if subscription.is_valid():
        tier = subscription.plan.product.account_tier
    else:
        tier = AccountTier.free_tier()

    account = subscription.customer.account
    account.tier = tier
    account.save()


@webhooks.handler("customer.subscription.deleted")
def subscription_deleted(event, **kwargs):
    """
    When the subscription is deleted, put the account on the free tier.
    """
    from accounts.models import AccountTier

    subscription = Subscription.objects.get(id=event.data["object"]["id"])

    account = subscription.customer.account
    account.tier = AccountTier.free_tier()
    account.save()
