import pytest

from projects.models.projects import ProjectRole


def test_project_role_from_string():
    assert ProjectRole.from_string("author") == ProjectRole.AUTHOR
    assert ProjectRole.from_string("AUTHOR") == ProjectRole.AUTHOR
    assert ProjectRole.from_string("AutHOr") == ProjectRole.AUTHOR
    with pytest.raises(ValueError, match='No project role matching "foo"'):
        ProjectRole.from_string("foo")


def test_project_role_and_above():
    assert ProjectRole.and_above(ProjectRole.AUTHOR) == [
        ProjectRole.AUTHOR,
        ProjectRole.MANAGER,
        ProjectRole.OWNER,
    ]
    assert ProjectRole.and_above(ProjectRole.MANAGER) == [
        ProjectRole.MANAGER,
        ProjectRole.OWNER,
    ]
    assert ProjectRole.and_above(ProjectRole.OWNER) == [
        ProjectRole.OWNER,
    ]
