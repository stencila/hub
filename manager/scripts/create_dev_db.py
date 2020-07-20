import io
import mimetypes
import random

from allauth.account.models import EmailAddress
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone

from accounts.models import Account, AccountRole, AccountTeam, AccountUser
from jobs.models import Queue, Worker, Zone
from manager.themes import Themes
from projects.models.files import File
from projects.models.projects import Project, ProjectAgent, ProjectRole
from projects.models.sources import (
    ElifeSource,
    GithubSource,
    GoogleDocsSource,
    UploadSource,
    UrlSource,
)
from users.models import User


def run(*args):
    """Create development database."""
    # Ensure that this is only used in development
    assert settings.DEBUG

    #################################################################
    # Users
    #################################################################

    # Admin (super user)
    admin = User.objects.create_user(
        username="admin",
        password="admin",
        first_name="Admin",
        email="admin@example.com",
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    # Staff member (not super user, but can access admin interface)
    staff = User.objects.create_user(
        username="staff",
        password="staff",
        first_name="Staff",
        email="staff@example.com",
    )
    staff.is_staff = True
    staff.save()

    for spec in [
        # Generic users that are added to EVERY account in these different roles
        ("a-user", "A", "User"),
        ("member", "Member", "User"),
        ("manager", "Manager", "User"),
        ("owner", "Owner", "User"),
        # Example users
        ("amitabh", "Amitabh", "Modi"),
        ("anna", "Anna", "Andersson"),
        ("daniel", "Daniel", "Colreavy"),
        ("zahra", "Zahra", "Temitope"),
    ]:
        User.objects.create_user(
            username=spec[0],
            password=spec[0],
            first_name=spec[1],
            last_name=spec[2],
            email=spec[0] + "@example.com",
        )

    member = User.objects.get(username="member")
    manager = User.objects.get(username="manager")
    owner = User.objects.get(username="owner")

    # Add varying amounts of profile data for these example users

    amitabh = User.objects.get(username="amitabh")
    amitabh.personal_account.location = "Sydney, Australia"
    amitabh.personal_account.image.save(
        "amitabh.png", open("scripts/data/amitabh.png", "rb")
    )
    EmailAddress.objects.create(
        user=amitabh, email="amitabh@example.org", verified=False, primary=True
    )

    anna = User.objects.get(username="anna")
    anna.personal_account.display_name = "Dr Anna Andersson"
    anna.personal_account.location = "Stockholm, Sweden"
    anna.personal_account.website = "https://anna.example.edu/profile.html"
    anna.personal_account.email = "anna@example.edu"
    anna.personal_account.image.save("anna.png", open("scripts/data/anna.png", "rb"))
    EmailAddress.objects.create(
        user=anna, email="anna@example.edu", verified=True, primary=True
    )
    EmailAddress.objects.create(
        user=anna, email="anna.andersson@example.com", verified=False, primary=False
    )

    daniel = User.objects.get(username="daniel")
    daniel.personal_account.location = "Dublin"
    daniel.personal_account.email = "daniel@example.edu"
    daniel.personal_account.image.save(
        "daniel.png", open("scripts/data/daniel.png", "rb")
    )

    zahra = User.objects.get(username="zahra")
    zahra.personal_account.location = "Nairobi, Kenya, East Africa"
    zahra.personal_account.website = "https://example.com"
    zahra.personal_account.image.save("zahra.png", open("scripts/data/zahra.png", "rb"))
    EmailAddress.objects.create(
        user=zahra, email="zahra@example.edu", verified=True, primary=True
    )
    EmailAddress.objects.create(
        user=zahra, email="zahra.temitope@example.com", verified=True, primary=False
    )
    EmailAddress.objects.create(
        user=zahra, email="zahrat@example.org", verified=False, primary=False
    )

    #################################################################
    # Accounts
    #################################################################

    # Generic and example organizations

    for name in ["an-org", "biotech-corp", "hapuku-university", "pewsey-publishing"]:
        account = Account.objects.create(name=name)

        # Add their image
        account.image.save(
            "account-logo.png", open("scripts/data/{0}.png".format(name), "rb")
        )

        # The generic users have their roles on every account
        AccountUser.objects.create(
            account=account, user=member, role=AccountRole.MEMBER.name
        )
        AccountUser.objects.create(
            account=account, user=manager, role=AccountRole.MANAGER.name
        )
        AccountUser.objects.create(
            account=account, user=owner, role=AccountRole.OWNER.name
        )

        # In addition, some other randome users are added with random roles
        for user in random_users():
            try:
                AccountUser.objects.create(
                    account=account, user=user, role=random_account_role()
                )
            except IntegrityError:
                pass

        # Each account has a "first-team" team with the generic users, plus a random
        # number of random users
        team1 = AccountTeam.objects.create(account=account, name="first-team")
        team1.members.set([member, owner, manager] + random_users())

        # Each account has a random number of others teams each
        # with a random name and random number of random users
        # (who don't need to be be users of the organizations)
        for index in range(random.randint(1, 5)):
            team = AccountTeam.objects.create(account=account, name=random_team_name())
            team.members.set(random_users())

    anorg = Account.objects.get(name="an-org")
    anorg.display_name = "An Organization"
    anorg.location = "Earth"
    anorg.website = "https://example.org"
    anorg.email = "contact@example.org"
    anorg.save()

    biotech = Account.objects.get(name="biotech-corp")
    biotech.display_name = "Biotech Corporation"
    biotech.location = "Portland, USA"
    biotech.website = "https://biotech.example.com"
    biotech.email = "contact@biotech.example.com"
    biotech.save()

    hapuku = Account.objects.get(name="hapuku-university")
    hapuku.display_name = "Hapuku University"
    hapuku.location = "Hapuku, Kaikoura, New Zealand"
    hapuku.website = "https://hapuku.example.edu"
    hapuku.email = "contact@hapuku.example.edu"
    hapuku.save()

    pewsey = Account.objects.get(name="pewsey-publishing")
    pewsey.display_name = "Pewsey Publishing"
    pewsey.location = "UK"
    pewsey.website = "https://pewsey.example.com"
    pewsey.email = "contact@pewsey.example.com"
    pewsey.save()

    #################################################################
    # Projects
    #################################################################

    # Each account has one private and one public project which
    # the generic `member`, `manager` etc accounts all have access to
    # at the corresponding levels

    for account in Account.objects.all().exclude(name__in=("stencila", "temp")):
        public = Project.objects.create(
            name="first-project",
            title="First project",
            account=account,
            creator=random_account_user(account),
            public=True,
            description="A public project for account {0}.".format(account.name),
            theme=random_theme(),
        )

        private = Project.objects.create(
            name="second-project",
            title="Second project",
            account=account,
            creator=random_account_user(account),
            public=False,
            description="A private project for account {0}.".format(account.name),
            theme=None,  # For private projects, will fallback to account theme
        )

        for project in [public, private]:
            # The generic users have their roles on these project
            for user, role in [
                (member, ProjectRole.AUTHOR.name),
                (manager, ProjectRole.MANAGER.name),
                (owner, ProjectRole.OWNER.name),
            ]:
                # Each user can only have a single role on a project, so check none already
                if ProjectAgent.objects.filter(project=project, user=user).count() == 0:
                    ProjectAgent.objects.create(project=project, user=user, role=role)

    #################################################################
    # Sources
    #################################################################

    for project in Project.objects.all():

        # Each project has an uploaded main.md file with some actual
        # content so we can test conversions and themeing etc on it

        create_main_file_for_project(project)

        # Each project has at least one of each type of source

        elife = ElifeSource.objects.create(
            project=project,
            creator=random_project_user(project),
            path="elife-article-5000",
            article=5000,
        )
        create_files_for_source(
            elife, ["elife5000.xml", "elife5000.xml.media/fig1.jpeg"]
        )

        github = GithubSource.objects.create(
            project=project,
            creator=random_project_user(project),
            path="stencila-test-repo",
            repo="stencila/test",
        )
        create_files_for_source(github, ["README.md", "sub/README.md"])

        GithubSource.objects.create(
            project=project,
            creator=random_project_user(project),
            path="star-wars-data",
            repo="evelinag/StarWars-social-network",
            subpath="data",
        )

        gdoc = GoogleDocsSource.objects.create(
            project=project,
            creator=random_project_user(project),
            path="google-docs-source",
            doc_id="gdoc-{}".format(project.name),
        )
        create_files_for_source(gdoc, ["google-docs-source.gdoc"])

        url = UrlSource.objects.create(
            project=project,
            creator=random_project_user(project),
            path="example-dot-org",
            url="https://example.org",
        )
        create_files_for_source(url, ["example-dot-org.html"])

        url = UrlSource.objects.create(
            creator=random_project_user(project),
            project=project,
            path="sub/subsub/mtcars.csv",
            url="https://raw.githubusercontent.com/curran/data/gh-pages/Rdatasets/csv/datasets/mtcars.csv",
        )
        create_files_for_source(url, ["sub/subsub/mtcars.csv"])

    #################################################################
    # Jobs, queues, workers, zones
    #################################################################

    # Each account...
    for account in Account.objects.all():

        zone = Zone.objects.create(account=account, name="first-zone")

        queue = Queue.objects.create(zone=zone, name="first-queue")

        worker = Worker.objects.create(hostname="first-worker")
        worker.queues.add(queue)


def random_users(num=None):
    """Get a random set of users."""
    all = User.objects.order_by("?").all()
    if num is None:
        num = random.randint(1, len(all))
    return all[:num]


def random_account_user(account):
    """Get a random user for an account."""
    account_user = AccountUser.objects.filter(account=account).order_by("?").first()
    return account_user.user if account_user else None


def random_account_role():
    """Get a random account role."""
    return random.choice([e.name for e in AccountRole])


def random_team_name():
    """Get a random team name."""
    return random.choice(
        ["editors", "authors", "reviewers", "special-project-team", "vision-2020-team"]
    )


def random_project_user(project):
    """Get a random user for an project."""
    return (
        ProjectAgent.objects.filter(project=project, user__isnull=False)
        .order_by("?")
        .first()
        .user
    )


def random_theme():
    """Get a randome theme name."""
    return random.choice([enum.value for enum in Themes])


with open("scripts/data/main.md") as file:
    main_markdown = file.read()


def create_main_file_for_project(project):
    """Create a main.md file for the project."""
    content = main_markdown.format(title=project.title, description=project.description)

    upload = UploadSource.objects.create(
        project=project, creator=project.creator, path="main.md"
    )
    upload.file.save(upload.path, io.StringIO(content))

    file = File.objects.create(
        project=project,
        source=upload,
        path="main.md",
        size=len(content),
        mimetype="text/markdown",
        modified=timezone.now(),
    )

    project.main = file
    project.save()


def create_files_for_source(source, paths):
    """Create files for a project source (i.e. simulate a pull)."""
    for path in paths:
        mimetype, encoding = mimetypes.guess_type(path)
        File.objects.create(
            project=source.project,
            source=source,
            path=path,
            size=random.lognormvariate(10, 2),
            mimetype=mimetype,
            encoding=encoding,
            modified=timezone.now(),
        )
