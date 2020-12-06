import logging
from typing import Union

import httpx
from celery import shared_task
from django import conf

from users.api.serializers import MeSerializer
from users.models import User, get_email

logger = logging.getLogger(__name__)


@shared_task
def update_services_all_users(services=["userflow"]):
    """
    Update external services for all users.
    """
    users = User.objects.select_related("personal_account").prefetch_related(
        "projects", "accounts"
    )
    for user in users:
        try:
            update_services_for_user(user, services)
        except Exception:
            logger.warning(
                "Exception while updating external services for user",
                exc_info=True,
                extra={"user": user},
            )


@shared_task
def update_services_for_user(user: Union[User, int], services=["userflow"]):
    """
    Update external services with latest values of a user's attributes.

    If the user has turned off the related feature, then the service will not be updated.
    """
    if isinstance(user, int):
        user = (
            User.objects.select_related("personal_account")
            .prefetch_related("projects", "accounts")
            .get(id=user)
        )

    data = MeSerializer(user).data
    feature_flags = data["feature_flags"]

    if "userflow" in services and feature_flags.get("product_tours", "on") == "on":
        update_userflow(user, data)


def update_userflow(user: User, data: dict):
    """
    Update UserFlow data for a user.

    See https://getuserflow.com/docs/api#create-or-update-a-user
    """
    # UserFlow can take arbitrary user data but it is
    # necessary to flatten it into a dictionary
    attributes = {}
    for name, value in data.items():
        if isinstance(value, dict):
            for subname, subvalue in value.items():
                attributes[f"{name}_{subname}"] = subvalue
        else:
            attributes[name] = value

    # UserFlow "expects" some attributes (shows them in
    # their interface by default), so provide them:
    # `name`, `email`
    name = user.username
    if name:
        attributes["name"] = name
    email = get_email(user)
    if email:
        attributes["email"] = email

    # Remove attributes we don't want to send
    del attributes["id"]
    del attributes["public_email"]
    del attributes["email_addresses"]
    del attributes["linked_accounts"]

    key = getattr(conf.settings, "USERFLOW_API_KEY", None)
    if key:
        response = httpx.post(
            "https://api.getuserflow.com/users",
            headers={
                "Authorization": f"Bearer {key}",
                "UserFlow-Version": "2020-01-03",
            },
            json={"id": user.id, "attributes": attributes},
        )
        response.raise_for_status()
