import typing

from django import template

from accounts.models import Account
from accounts.url_helpers import account_url_reverse

register = template.Library()


class AccountUrlNode(template.Node):
    account: template.Variable
    view_name: template.Variable
    args: typing.List[template.Variable]

    def __init__(self, view_name: str, account: str, args: str) -> None:
        self.account = template.Variable(account)
        self.view_name = template.Variable(view_name)
        self.args = list(map(template.Variable, args))

    def render(self, context):
        account: Account = self.account.resolve(context)
        if not isinstance(account, Account):
            raise TypeError('The first variable to the templatetag must be an Account instance.')

        view_name: str = self.view_name.resolve(context)

        if not isinstance(view_name, str):
            raise TypeError('The view name is expected to be a str')

        resolved_args = list(map(lambda a: a.resolve(context), self.args))

        return account_url_reverse(view_name, resolved_args, account=account)


@register.tag
def account_url(parser, token):
    try:
        tag_name, view_name, account, *args = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires at least two args" % token.contents.split()[0]
        )

    return AccountUrlNode(view_name, account, args)
