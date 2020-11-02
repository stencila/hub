from celery import shared_task

from accounts.models import Account


@shared_task
def set_image_from_url(account_id: int, url: str):
    """
    Set the image of an account from a URL.
    """
    account = Account.objects.get(id=account_id)
    account.set_image_from_url(url)


@shared_task
def set_image_from_socialaccount(account_id: int, provider: str):
    """
    Set the image of an account from a social account.
    """
    account = Account.objects.get(id=account_id)
    account.set_image_from_socialaccount(provider)


@shared_task
def set_image_from_socialaccounts(account_id: int):
    """
    Set the image of an account from one of its social accounts.
    """
    account = Account.objects.get(id=account_id)
    account.set_image_from_socialaccounts()
