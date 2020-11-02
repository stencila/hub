from celery import shared_task

from accounts.models import Account


@shared_task
def set_image_from_socialaccount(account_id: int, provider: str):
    """
    Set the image of a personal account a social account image.
    """
    account = Account.objects.get(id=account_id)
    account.set_image_from_socialaccount(provider)


@shared_task
def set_image_from_socialaccounts(account_id: int):
    """
    Set the image of a personal account from social account images.
    """
    account = Account.objects.get(id=account_id)
    account.set_image_from_socialaccounts()
