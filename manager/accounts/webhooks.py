"""
Custom webhooks to add behavior when subscriptions change.

Note that the `djstripe` webhooks already do the syncing of data (ie. Stripe
to database).

To test these webhooks sync the db and run the Stripe CLI client:

    make sync-devdb-stripe

Then set the webhook signing secret displayed as an environment variable in the
`.secrets` file (don't commit that change!)

    make run

Finally, in the admin interface link the `AccountTier`s to the Stripe `Product`s.
"""

from djstripe import webhooks
from djstripe.models import Customer, Subscription


@webhooks.handler("customer.updated")
def customer_updated(event, **kwargs):
    """
    When customer updates billing information on Stripe, transfer to account fields.
    """
    customer = Customer.objects.get(id=event.data["object"]["id"])

    account = customer.account
    account.billing_email = customer.email
    account.save()

@webhooks.handler("customer.subscription.created", "customer.subscription.updated")
def subscription_updated(event, **kwargs):
    """
    When the subscription is created (e.g. manually in the Stripe
    Dashboard) or updated (e.g. via the Stripe Customer Portal),
    change the account's tier.
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
