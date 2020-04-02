from django.test import TestCase

from projects.permission_models import get_highest_permission, ProjectPermissionType


class ProjectPermissionTests(TestCase):
    def test_get_highest_permissions(self):
        """Various tests to ensure the highest permission is always found in a list of permissions."""
        self.assertIsNone(
            get_highest_permission([])
        )  # return None if no permissions passed in

        self.assertEqual(
            ProjectPermissionType.OWN,
            get_highest_permission(
                [
                    ProjectPermissionType.EDIT,
                    ProjectPermissionType.MANAGE,
                    ProjectPermissionType.OWN,
                ]
            ),
        )

        self.assertEqual(
            ProjectPermissionType.MANAGE,
            get_highest_permission(
                [
                    ProjectPermissionType.VIEW,
                    ProjectPermissionType.EDIT,
                    ProjectPermissionType.MANAGE,
                ]
            ),
        )

        self.assertEqual(
            ProjectPermissionType.VIEW,
            get_highest_permission([ProjectPermissionType.VIEW]),
        )

    def test_permission_comparison(self):
        """
        Test that comparison between `ProjectPermissionType`s works as expected,
        e.g.`ProjectPermissionType.VIEW` < `ProjectPermissionType.OWN`
        """
        self.assertEqual(
            ProjectPermissionType.VIEW, ProjectPermissionType.VIEW
        )  # Make sure equality wasn't broken

        self.assertLess(ProjectPermissionType.VIEW, ProjectPermissionType.MANAGE)
        self.assertLess(ProjectPermissionType.MANAGE, ProjectPermissionType.OWN)

        self.assertGreater(ProjectPermissionType.EDIT, ProjectPermissionType.VIEW)
        self.assertGreater(ProjectPermissionType.EDIT, ProjectPermissionType.SUGGEST)

        self.assertGreaterEqual(ProjectPermissionType.EDIT, ProjectPermissionType.EDIT)
        self.assertLessEqual(ProjectPermissionType.MANAGE, ProjectPermissionType.MANAGE)
