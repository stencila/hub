from rest_framework import renderers, status

from manager.testing import DatabaseTestCase


class NodeViewsTest(DatabaseTestCase):
    """Test creating and retrieving nodes."""

    # Type specific CRUD methods for Nodes

    def create_node(self, user=None, project=None, node=None):
        return self.create(
            user,
            "nodes",
            data={"project": project, "node": node},
            headers={"HTTP_ACCEPT": "application/json"},
        )

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

    # Testing methods

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
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_must_have_project_edit_permission(self):
        response = self.create_node(self.ada, self.bob_private.id, 42)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_must_have_required_fields(self):
        response = self.create(
            self.ada, "nodes", headers={"HTTP_ACCEPT": "application/json"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "message": "Invalid input.",
            "errors": [{"field": "node", "message": "This field is required."}],
        }

    def test_create_host_must_be_url(self):
        response = self.create(
            self.ada,
            "nodes",
            data={"node": 41, "host": "foo"},
            headers={"HTTP_ACCEPT": "application/json"},
        )
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

    def test_retrieve_json(self):
        key = self.create_node(self.ada, self.ada_public.id, "A").data["key"]
        response = self.retrieve_json(None, key)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_json_when_no_project(self):
        key = self.create_node(self.ada, None, "A").data["key"]

        for user in (self.ada, self.bob):
            response = self.retrieve_json(self.ada, key)
            assert response.status_code == status.HTTP_200_OK

    def test_retrieve_html_ok(self):
        key = self.create_node(self.ada, self.ada_private.id, "C").data["key"]
        response = self.retrieve_html(self.ada, key)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.accepted_renderer, renderers.TemplateHTMLRenderer)
        assert response.template_name == "projects/nodes/retrieve.html"
        assert response.data.get("html") is not None

    def test_retrieve_anything(self):
        """Test that if Accept:*/* or no Accept header that get HTML."""
        key = self.create_node(self.ada, self.ada_private.id, "A node").data["key"]

        response = self.retrieve(self.ada, "nodes", kwargs={"key": key})
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.accepted_renderer, renderers.TemplateHTMLRenderer)

        response = self.retrieve(
            self.ada, "nodes", kwargs={"key": key}, headers={"HTTP_ACCEPT": "*/*"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.accepted_renderer, renderers.TemplateHTMLRenderer)

    def test_retrieve_html_when_no_project(self):
        """Test that everyone gets complete view for any node with no project specified."""
        key = self.create_node(self.ada, None, "A").data["key"]

        for user in (self.ada, self.bob, None):
            response = self.retrieve_html(user, key)
            assert response.template_name == "projects/nodes/retrieve.html"
