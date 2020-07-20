import shortuuid
from django.core.management.base import BaseCommand
from django.db import transaction
from django_super_deduper.merge import MergedModelInstance

from accounts.models import Account
from projects.models.projects import Project
from users.models import User


class Command(BaseCommand):
    """
    A management command to merge users.

    This may be necessary when a user has signed in using different methods
    e.g. using Google and username/password. There are some mechanisms to
    avoid duplication in these instances. But this script allows for de-duplication
    where this has not been successful.

    Use with caution, testing and checking!

    Example usage:

    # Merge users "foo" and "bar" into user "baz"
    ./venv/bin/python3 manage.py merge_users baz foo bar
    """

    help = "Merges users for de-duplication purposes."

    def add_arguments(self, parser):
        """
        Add arguments for this command.
        """
        parser.add_argument(
            "primary_username", type=str, help="The user to merge other user data into."
        )
        parser.add_argument(
            "secondary_usernames",
            nargs="+",
            type=str,
            help="The other users to merge into the primary user.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Handle the command (ie. execute it).
        """
        primary_username = options["primary_username"]
        secondary_usernames = options["secondary_usernames"]

        self.stdout.write(
            self.style.WARNING(
                "Are you sure you want to merge users {secondary} into user {primary}? "
                "This will delete {secondary}. (y/n)".format(
                    primary=primary_username, secondary=", ".join(secondary_usernames)
                )
            )
        )
        if input("> ") != "y":
            self.stdout.write(self.style.WARNING("Cancelled."))
            return

        # To avoid clashes in project names (which will cause them to be dropped)
        # check for duplicate project names attached to the users personal account
        # and append a unique string to any duplicates
        existing_names = Project.objects.filter(
            account__user__username=primary_username
        ).values_list("name", flat=True)
        secondary_projects = Project.objects.filter(
            account__user__username__in=secondary_usernames
        )
        for project in secondary_projects:
            if project.name in existing_names:
                project.name += "-" + shortuuid.ShortUUID().random(length=8)
                project.save()

        # Merge the users' personal accounts
        primary_account = Account.objects.get(user__username=primary_username)
        secondary_accounts = Account.objects.filter(
            user__username__in=secondary_usernames
        )
        MergedModelInstance.create(
            primary_account, secondary_accounts, keep_old=False,
        )

        # Merge the users
        primary_user = User.objects.get(username=primary_username)
        secondary_users = User.objects.filter(username__in=secondary_usernames)
        MergedModelInstance.create(primary_user, secondary_users, keep_old=False)

        self.stdout.write(self.style.SUCCESS("Succeeded."))
