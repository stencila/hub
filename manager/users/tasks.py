from typing import Union

import httpx
from celery import shared_task
from django import conf

from users.api.serializers import MeSerializer
from users.models import User


@shared_task
def update_services_all_users(services=["userflow"]):
    """
    Update external services for all users.
    """
    users = User.objects.select_related("personal_account").prefetch_related(
        "projects", "accounts"
    )
    for user in users:
        update_services_for_user(user, services)


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

    # Remove attributes we don't want to send
    del attributes["id"]
    del attributes["email_addresses"]
    del attributes["linked_accounts"]

    key = getattr(conf.settings, "USERFLOW_API_KEY", None)
    if key:
        httpx.post(
            "https:/api.getuserflow.com/users",
            headers={
                "Authorization": f"Bearer {key}",
                "UserFlow-Version": "2020-01-03",
            },
            data={"id": user.id, "attributes": attributes},
        )
