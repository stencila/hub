import datetime
import io
import math
import mimetypes
import os
import random
from pathlib import Path

from allauth.account.models import EmailAddress
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.timezone import utc
from djstripe.models import Price, Product
from faker import Faker
from stencila.schema.json import object_encode
from stencila.schema.types import (
    Article,
    CodeChunk,
    CodeExpression,
    MathBlock,
    MathFragment,
)

from accounts.models import Account, AccountRole, AccountTeam, AccountTier, AccountUser
from dois.models import Doi
from jobs.models import Job, JobMethod, JobStatus, Queue, Worker, Zone
from manager.themes import Themes
from projects.models.files import File
from projects.models.nodes import Node
from projects.models.projects import Project, ProjectAgent, ProjectRole
from projects.models.reviews import Review, ReviewStatus
from projects.models.sources import (
    ElifeSource,
    GithubSource,
    GoogleDocsSource,
    Source,
    UploadSource,
    UrlSource,
)
from users.models import User

fake = Faker(["en_US", "it_IT", "ja_JP"])


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

    # Account tiers, products and prices

    for tier in range(1, 6):
        active = tier < 4

        # Associated product and price (in prod these object are created in the Stripe
        # dashboard and synced using `./venv/bin/python3 manage.py djstripe_sync_models`)
        if active:
            product = Product.objects.create(
                id=f"product_tier{tier}", name=f"Tier {tier} Product"
            )
            Price.objects.create(
                id=f"price_tier{tier}",
                product=product,
                active=True,
                currency="usd",
                unit_amount=(tier - 1) * 1000,
            )
        else:
            product = None

        # Account tier
        if tier == 1:
            # Tier 1 is created in a data migration, so we just set it's other details
            AccountTier.objects.update(
                id=1, name="Tier 1", product=product, summary=fake.sentence()
            )
        else:
            AccountTier.objects.create(
                name=f"Tier {tier}",
                product=product,
                active=active,
                summary=fake.sentence(),
            )

    # Generic and example organizations

    for name in ["an-org", "biotech-corp", "hapuku-university", "pewsey-publishing"]:
        account = Account.objects.create(name=name, tier=random_account_tier())

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
            description=(
                f"A public project for account {account.name}. "
                + fake.paragraph(nb_sentences=5)
            )
            if fake.boolean(70)
            else None,
            theme=random_enum_value(Themes).name,
        )

        private = Project.objects.create(
            name="second-project",
            title="Second project",
            account=account,
            creator=random_account_user(account),
            public=False,
            description=(
                f"A private project for account {account.name}. "
                + fake.paragraph(nb_sentences=5)
            )
            if fake.boolean(70)
            else None,
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

    for index, project in enumerate(Project.objects.all()):

        # Each project has an uploaded main.md file with some actual
        # content so we can test conversions and themeing etc on it

        create_main_file_for_project(project)

        # Projects have varying of the following source

        if index % 6 == 1:
            elife = ElifeSource.objects.create(
                project=project,
                creator=random_project_user(project),
                path="elife-article-5000",
                article=5000,
            )
            create_files_for_source(
                elife, ["elife5000.xml", "elife5000.xml.media/fig1.jpeg"]
            )

        if index % 6 == 2:
            github = GithubSource.objects.create(
                project=project,
                creator=random_project_user(project),
                path="stencila-test-repo",
                repo="stencila/test",
            )
            create_files_for_source(github, ["README.md", "sub/README.md"])

        if index % 6 == 3:
            GithubSource.objects.create(
                project=project,
                creator=random_project_user(project),
                path="star-wars-data",
                repo="evelinag/StarWars-social-network",
                subpath="data",
            )

        if index % 6 == 4:
            gdoc = GoogleDocsSource.objects.create(
                project=project,
                creator=random_project_user(project),
                path="google-docs-source",
                doc_id="gdoc-{}".format(project.name),
            )
            create_files_for_source(gdoc, ["google-docs-source.gdoc"])

        if index % 6 == 5:
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
    # Nodes
    #################################################################

    for project in Project.objects.all():
        create_nodes_for_project(project)

    #################################################################
    # Reviews
    #################################################################

    for project in Project.objects.all():
        create_reviews_for_project(project)

    #################################################################
    # Jobs, queues, workers, zones
    #################################################################

    # Each account...
    for account in Account.objects.all():

        zone = Zone.objects.create(account=account, name="first-zone")

        queue = Queue.objects.create(zone=zone, name="first-queue")

        worker = Worker.objects.create(hostname="first-worker")
        worker.queues.add(queue)

    # Each project...
    for project in Project.objects.all():
        jobs = random.uniform(-1, 5)
        jobs = 0 if jobs < 0 else int(math.exp(jobs))
        for index in range(jobs):
            method = fake.random_element(JobMethod).name
            status = fake.random_element(JobStatus).name
            description = f"{method.title()} {fake.sentence(nb_words=5)}"
            creator = random_project_user(project)
            began = fake.date_time_between(start_date="-2y", tzinfo=utc)
            ended = began + datetime.timedelta(seconds=random.lognormvariate(5, 3))
            Job.objects.create(
                project=project,
                description=description,
                creator=creator,
                began=began,
                ended=ended,
                status=status,
                method=method,
            )


def random_users(num=None):
    """Get a random set of users."""
    all = User.objects.order_by("?").all()
    if num is None:
        num = random.randint(1, len(all))
    return all[:num]


def random_user():
    """Get a random user."""
    return User.objects.order_by("?").first()


def random_account_tier():
    """Get a random account tier."""
    return AccountTier.objects.filter(active=True).order_by("?").first()


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
    """Get a random user for n project."""
    return (
        ProjectAgent.objects.filter(project=project, user__isnull=False)
        .order_by("?")
        .first()
        .user
    )


def random_project_source(project):
    """Get a random source for a project."""
    return Source.objects.filter(project=project).order_by("?").first()


def random_enum_value(enum):
    """Get a random enum value."""
    return random.choice([value for value in enum])


with open("scripts/data/main.md") as file:
    main_markdown = file.read()


def create_main_file_for_project(project):
    """Create a main.md file for the project."""
    content = main_markdown.format(title=project.title, description=project.description)

    # The upload that is the source of the file
    upload = UploadSource.objects.create(
        project=project, creator=project.creator, path="main.md"
    )
    upload.file.save(upload.path, io.StringIO(content))

    # The uploaded file in the working directory
    path = project.STORAGE.path(project.file_location("main.md"))
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

    # The file object that was created by pulling the file
    File.objects.create(
        project=project,
        source=upload,
        path="main.md",
        size=len(content),
        mimetype="text/markdown",
        modified=timezone.now(),
    )

    # Make it the main file
    project.main = "main.md"
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


def create_nodes_for_project(project):
    """
    Create some nodes for a project.

    The purpose of this is mainly to able to be able to preview
    the HTML templates used for `Nodes` with real-ish data.

    Generates the same nodes for every project (so you can
    view them regardless of which test user you are logged in
    as).
    """

    nodes = [
        Article(),
        CodeChunk(programmingLanguage="r", text="plot(mtcars)"),
        CodeExpression(programmingLanguage="js", text="x * y"),
        MathBlock(mathLanguage="tex", text="\\int\\limits_a^b x^2  \\mathrm{d} x"),
        MathFragment(mathLanguage="asciimath", text="2 pi r"),
    ]

    for node in nodes:
        Node.objects.create(
            project=project,
            app="gsuita",
            host="https://example.com/some-doc",
            json=object_encode(node),
        )


def create_reviews_for_project(project):
    """
    Create some reviews for a project.

    The purpose of this is mainly to able to be able to preview
    the HTML templates used for `Review`s with real-ish data.
    """

    for index in range(10):
        reviewer_is_user = fake.boolean(70)

        status = (
            random_enum_value(ReviewStatus).name
            if index > 4
            else ReviewStatus.EXTRACTED.name
        )
        if status == ReviewStatus.EXTRACTED.name:
            para1 = fake.paragraph(nb_sentences=10)
            review_node = Node.objects.create(
                project=project,
                json=dict(
                    type="Review", content=[dict(type="Paragraph", content=[para1])]
                ),
            )
            review_author_name = fake.name()
            review_date = fake.date_time_this_month(tzinfo=utc)
            review_title = fake.sentence() if fake.boolean(70) else None
            review_description = para1
            review_comments = random.randint(0, 142)

            if fake.boolean():
                deposited = (
                    fake.date_time_this_month(tzinfo=utc) if fake.boolean(80) else None
                )
                deposit_success = bool(deposited and fake.boolean(80))

                registered = (
                    fake.date_time_this_month(tzinfo=utc)
                    if deposit_success and fake.boolean(80)
                    else None
                )
                registration_success = bool(registered and fake.boolean(80))

                Doi.objects.create(
                    node=review_node,
                    deposited=deposited,
                    deposit_success=deposit_success,
                    registered=registered,
                    registration_success=registration_success,
                )
        else:
            review_node = None
            review_author_name = None
            review_date = None
            review_title = None
            review_description = None
            review_comments = None

        Review.objects.create(
            project=project,
            creator=random_project_user(project),
            status=status,
            source=random_project_source(project),
            reviewer=random_user() if reviewer_is_user else None,
            reviewer_email="reviewer@example.org" if reviewer_is_user else None,
            request_message=fake.paragraph(),
            cancel_message=fake.paragraph()
            if status == ReviewStatus.CANCELLED.name and fake.boolean(70)
            else None,
            response_message=fake.paragraph()
            if status in (ReviewStatus.ACCEPTED.name, ReviewStatus.DECLINED.name)
            and fake.boolean(50)
            else None,
            review=review_node,
            review_author_name=review_author_name,
            review_date=review_date,
            review_title=review_title,
            review_description=review_description,
            review_comments=review_comments,
        )
