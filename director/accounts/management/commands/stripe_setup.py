import json
import logging

import stripe
from django.core.management import BaseCommand
from djstripe import settings as djstripe_settings
from djstripe.models import Plan, Product, Subscription

from accounts.management.commands.stripe_setup_config import DEFAULT_CURRENCY, PLAN_DEFINITIONS, PlanDefinitionKey
from accounts.models import ProductExtension, AccountSubscription

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

PRODUCT_NAMES = [p[PlanDefinitionKey.NAME].value for p in PLAN_DEFINITIONS]


def product_name_to_plan_name(product_name: str) -> str:
    return '{} Plan'.format(product_name)


PLAN_NAMES = list(map(product_name_to_plan_name, PRODUCT_NAMES))


def remote_product_cleanup():
    """Go through remote Products and remove those that are not in the local list of products."""
    for remote_product in Product.api_list():
        if remote_product['name'] in PRODUCT_NAMES:
            active = True
        else:
            active = False

        stripe.Product.modify(remote_product['id'], api_key=djstripe_settings.STRIPE_SECRET_KEY, active=active)
        LOGGER.info('Remote Product %s made %s', remote_product['name'], 'active' if active else 'inactive')


def remote_plan_cleanup():
    """Go through the remote plans and remove thos that are not in the local list of plans."""
    for remote_plan in Plan.api_list():
        if remote_plan['nickname'] in PLAN_NAMES:
            active = True
        else:
            active = False
        stripe.Plan.modify(remote_plan['id'], api_key=djstripe_settings.STRIPE_SECRET_KEY, active=active)
        LOGGER.info('Remote Plan %s made %s', remote_plan['nickname'], 'active' if active else 'inactive')


def setup_remote_product(name: str, description: str) -> stripe.Product:
    product_to_save = {}
    create = True

    for remote_product in Product.api_list():
        if remote_product['name'] == name:
            product_to_save = remote_product
            create = False

    product_to_save['name'] = name
    product_to_save['type'] = 'service'
    product_to_save['statement_descriptor'] = name.upper()
    product_to_save['description'] = description

    if create:
        return stripe.Product.create(api_key=djstripe_settings.STRIPE_SECRET_KEY, **product_to_save)

    for k in ('object', 'created', 'livemode', 'type', 'updated'):
        if k in product_to_save:  # These keys might come back from server but can't be written
            del product_to_save[k]

    sid = product_to_save['id']
    del product_to_save['id']

    return stripe.Product.modify(sid, api_key=djstripe_settings.STRIPE_SECRET_KEY, **product_to_save)


def setup_remote_plan(product: stripe.Product, plan_data: dict) -> stripe.Product:
    plan_nickname = product_name_to_plan_name(product['name'])

    plan_to_save = None
    create = True

    for remote_plan in Plan.api_list():
        if remote_plan['nickname'] == plan_nickname:
            plan_to_save = remote_plan
            create = False
            break

    if plan_to_save is None:
        plan_to_save = {}

    plan_to_save['interval'] = 'month'
    plan_to_save['nickname'] = plan_nickname
    plan_to_save['currency'] = DEFAULT_CURRENCY
    plan_to_save['amount_decimal'] = plan_data[PlanDefinitionKey.PRICE]

    if create:
        plan_to_save['product'] = product['id']
        return stripe.Plan.create(api_key=djstripe_settings.STRIPE_SECRET_KEY, **plan_to_save)

    for k in ('amount', 'object', 'created', 'livemode', 'amount_decimal', 'billing_scheme', 'currency', 'interval',
              'interval_count', 'usage_type'):
        if k in plan_to_save:  # These keys might come back from server but can't be written
            del plan_to_save[k]

    sid = plan_to_save['id']
    del plan_to_save['id']

    if plan_to_save['product'] != product['id']:
        stripe.Plan.modify(sid, api_key=djstripe_settings.STRIPE_SECRET_KEY, product=product['id'])

    del plan_to_save['product']

    return stripe.Plan.modify(sid, api_key=djstripe_settings.STRIPE_SECRET_KEY, **plan_to_save)


def local_plan_cleanup():
    plans_to_remove = Plan.objects.exclude(nickname__in=PLAN_NAMES)

    subs_for_plans = Subscription.objects.filter(plan__in=plans_to_remove)

    AccountSubscription.objects.filter(subscription__in=subs_for_plans).delete()
    plans_to_remove.delete()


def local_product_cleanup():
    products_to_remove = Product.objects.exclude(name__in=PRODUCT_NAMES)
    ProductExtension.objects.filter(product__in=products_to_remove).delete()
    products_to_remove.delete()


def plan_setup():
    remote_plan_cleanup()
    remote_product_cleanup()
    local_plan_cleanup()
    local_product_cleanup()
    for plan_definition in PLAN_DEFINITIONS:
        stripe_product = setup_remote_product(plan_definition[PlanDefinitionKey.NAME].value,
                                              plan_definition[PlanDefinitionKey.DESCRIPTION])
        stripe_plan = setup_remote_plan(stripe_product, plan_definition)

        product = Product.sync_from_stripe_data(stripe_product)
        Plan.sync_from_stripe_data(stripe_plan)

        try:
            pe = ProductExtension.objects.get(product=product)
        except ProductExtension.DoesNotExist:
            pe = ProductExtension(product=product)

        pe.allowances = json.dumps(plan_definition[PlanDefinitionKey.QUOTA])
        pe.tag_line = plan_definition[PlanDefinitionKey.TAG_LINE]
        pe.save()


class Command(BaseCommand):
    help = 'Setup plans on Stripe'

    def handle(self, *args, **options):
        plan_setup()
