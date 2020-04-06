from django.db import models
from django.shortcuts import reverse
from jsonfallback.fields import FallbackJSONField

from projects.models import Project
from users.models import User


class Node(models.Model):
    """
    A document node.

    Could be any type of node e.g. `CodeChunk`, `CreativeWork`, `Number`.

    Each node has a unique `key` generated at the time of creation. This
    is the only way to retreive a node.

    Each node can be associated with a `project`. This is for authorization.
    Although the `key` is a secret, project based authorization adds an additional
    layer of security e.g. in case of accidental leakage of a node URL.
    This field does not use cascading delete because node URLs
    should be permananent. The `project` is not required. This allows
    apps to create nodes in documents (e.g. GSuita) or to or to convert documents
    (e.g. Encoda) without having to associate them with a project.

    Each node is created by an `app`. This string is primarily used when generating
    HTML representations of the node to provide links back to that app.

    A node is usually created within a `host`. This is a URL that is primarily used
    when generating HTML representations of the node to provide links back to the
    document.

    The `json` of the node is also immutable. It is returned to requests with
    `Accept: application/json` (if authorized).
    """

    class Meta:
        unique_together = (
            "project",
            "key",
        )

    creator = models.ForeignKey(
        User,
        null=True,  # Should only be null if the creator is deleted
        blank=True,
        on_delete=models.SET_NULL,
        related_name="nodes_created",
        help_text="User who created the project.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="When the project was created."
    )

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="nodes",
        help_text="The project this node is associated with.",
    )

    app = models.TextField(
        null=True,
        blank=True,
        help_text="An identifier for the app that created the node.",
    )

    host = models.URLField(
        null=True,
        blank=True,
        help_text="URL of the host document within which the node was created.",
    )

    key = models.TextField(db_index=True, help_text="The key to the node")

    json = FallbackJSONField(help_text="The JSON content of node.")

    def get_absolute_url(self):
        return reverse("api-nodes-detail", kwargs={"key": self.key})
