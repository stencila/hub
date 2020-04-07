from rest_framework import status

from general.testing import DatabaseTestCase
from projects.api.views.nodes import node_type


class NodeViewsTest(DatabaseTestCase):
    """Test creating and retrieving nodes."""

    def create_node(self, user=None, project=None, node=None):
        return self.create(user, "nodes", {"project": project, "node": node})

    def retrieve_json(self, user, key):
        return self.retrieve(
            user,
            "nodes",
            kwargs={"key": key},
            headers={"HTTP_ACCEPT": "application/json"},
        )

    def retrieve_html(self, user, key):
        return self.retrieve(
            user, "nodes", kwargs={"key": key}, headers={"HTTP_ACCEPT": "text/html"},
        )

    def test_create_ok(self):
        node = {"type": "CodeChunk", "text": "plot(1, 1)"}

        response = self.create(self.ada, "nodes", {"node": node})
        assert response.status_code == status.HTTP_201_CREATED

        response = self.create(
            self.ada, "nodes", {"node": node, "project": self.ada_private.id}
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = self.create(
            self.ada,
            "nodes",
            {
                "node": node,
                "project": self.ada_public.id,
                "app": "an-app",
                "host": "http://example.org",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = self.create_node(self.ada, self.ada_public.id, node)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["key"] is not None
        assert response.data["url"] is not None

    def test_create_must_be_authenticated(self):
        response = self.create_node()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_must_have_project_edit_permission(self):
        response = self.create_node(self.ada, self.bob_private.id, 42)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_must_have_required_fields(self):
        response = self.create(self.ada, "nodes")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "message": "Invalid input.",
            "errors": [{"field": "node", "message": "This field is required."}],
        }

    def test_create_host_must_be_url(self):
        response = self.create(self.ada, "nodes", {"node": 41, "host": "foo"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "message": "Invalid input.",
            "errors": [{"field": "host", "message": "Enter a valid URL."}],
        }

    def test_retrieve_json_ok(self):
        key = self.create_node(self.ada, self.ada_public.id, 42).data["key"]
        response = self.retrieve_json(self.ada, key)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["creator"] is self.ada.id
        assert response.data["created"] is not None
        assert response.data["project"] == self.ada_public.id
        assert response.data["key"] == key
        assert response.data["node"] == 42

    def test_retrieve_json_is_unmodified(self):
        """Test that there is no modification to the node's JSON."""
        inp = {"property_a": 1, "property2": {"camelCased": None}}
        key = self.create_node(self.ada, None, inp).data["key"]
        out = self.retrieve_json(self.ada, key).data["node"]
        assert out == inp

    def test_retrieve_json_must_be_authenticated(self):
        key = self.create_node(self.ada, self.ada_public.id, "A").data["key"]
        response = self.retrieve_json(None, key)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_json_must_have_project_view_permission(self):
        key = self.create_node(self.ada, self.ada_private.id, "B").data["key"]
        response = self.retrieve_json(self.bob, key)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_json_when_no_project(self):
        key = self.create_node(self.ada, None, "A").data["key"]

        for user in (self.ada, self.bob):
            response = self.retrieve_json(self.ada, key)
            assert response.status_code == status.HTTP_200_OK

        # Anonymous users can't get JSON
        response = self.retrieve_json(None, key)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_html_ok(self):
        key = self.create_node(self.ada, self.ada_private.id, "C").data["key"]
        response = self.retrieve_html(self.ada, key)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("node_type") == "Text"
        assert response.data.get("html") is not None

    def test_retrieve_html_complete_for_public_projects(self):
        """Test users get complete view for public projects."""
        key = self.create_node(self.ada, self.ada_public.id, "A node").data["key"]
        assert self.retrieve_html(self.bob, key).data.get("html") is not None
        assert self.retrieve_html(None, key).data.get("html") is not None

    def test_retrieve_html_basic_for_private_projects(self):
        """Test users get basic view for private projects."""
        key = self.create_node(self.ada, self.ada_private.id, "Another node").data[
            "key"
        ]
        assert self.retrieve_html(self.bob, key).data.get("html") is None
        assert self.retrieve_html(None, key).data.get("html") is None

    def test_retrieve_html_when_no_project(self):
        """Test that everyone gets complete view for any node with no project specified."""
        key = self.create_node(self.ada, None, "A").data["key"]

        for user in (self.ada, self.bob, None):
            assert self.retrieve_html(user, key).data.get("html") is not None


def test_node_type():
    assert node_type(None) == "Null"
    assert node_type(True) == "Boolean"
    assert node_type(42) == "Number"
    assert node_type(3.14) == "Number"
    assert node_type("Hello") == "Text"
    assert node_type([]) == "Array"
    assert node_type(tuple()) == "Array"
    assert node_type({}) == "Object"
    assert node_type({"type": "CodeChunk"}) == "CodeChunk"
