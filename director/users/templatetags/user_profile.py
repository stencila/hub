from django import template

from accounts.models import Account

register = template.Library()


@register.simple_tag(takes_context=True, name="user_profile_link")
def user_profile_link(context, *args, **kwargs):
    user = context["user"]

    if user is None or not user.is_authenticated:
        return ""

    try:
        account = Account.objects.get(user__id=user.id)
        return "/{}/".format(account.name)
    except Account.DoesNotExist:
        return ""
