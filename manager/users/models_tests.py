from accounts.models import Account
from manager.testing import DatabaseTestCase
from projects.models.projects import Project, ProjectAgent
from projects.models.sources import ElifeSource
from users.models import get_custom_attributes


class UserFunctionsTests(DatabaseTestCase):
    def test_custom_attribute_elife_author(self):
        # Neither Ada or Bob are eLife authors
        attrs = get_custom_attributes(self.ada)
        assert attrs["elife_author"] is False
        attrs = get_custom_attributes(self.bob)
        assert attrs["elife_author"] is False

        # Ada creates a project and adds an eLife source to it
        project = Project.objects.create(account=self.ada.personal_account)
        ElifeSource.objects.create(project=project, article=1234)
        attrs = get_custom_attributes(self.ada)
        assert attrs["elife_author"] is True

        # Bob gets added as an author to a project owned by eLife
        elife = Account.objects.create(name="elife")
        project = Project.objects.create(account=elife)
        ProjectAgent.objects.create(project=project, user=self.bob, role="AUTHOR")
        attrs = get_custom_attributes(self.bob)
        assert attrs["elife_author"] is True
