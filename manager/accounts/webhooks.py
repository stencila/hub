"""

To test these webhooks see the docs (https://stripe.com/docs/webhooks/test) e.g.

    stripe listen --forward-to localhost:8000/stencila/stripe/webhook/

Then set the webook signing secret displayed as an environment variable

    set -x DJANGO_DJSTRIPE_WEBHOOK_SECRET whsec_r3lKX3vJgqmgLrJNLtVpDpPdIsoIm2Ew # fish shell
    make run
"""


from djstripe import webhooks
from djstripe.models import Subscription

@webhooks.handler("customer.subscription.updated")
def subscription_updated(event, **kwargs):
    """
    Change the account tier when the subscription is updated
    """
    from accounts.models import AccountTier
    
    subscription = Subscription.objects.get(id=event.data["object"]["id"])
    tier = AccountTier.objects.get(id=1)
    if subscription.is_valid():
        product = subscription.items.first().price.product
        # TODO: Get the account tier that this product relates to
        tier = AccountTier.objects.get(id=2)
    
    account = subscription.customer.account
    account.tier = tier
    account.save()

@webhooks.handler("customer.subscription.deleted")
def subscription_deleted(event, **kwargs):
    from accounts.models import AccountTier

    subscription = Subscription.objects.get(id=event.data["object"]["id"])
    print('subscription:', subscription, subscription.is_valid())
    account = subscription.customer.account
    # When the subscription is deleted (cancelled) place on
    # free tier
    account.tier = AccountTier.objects.get(id=1)
    account.save()
