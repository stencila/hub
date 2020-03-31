from django.db import models
from django.shortcuts import reverse

from projects.models import Project


class Node(models.Model):
    """
    A document node.

    Could be any type of node e.g. `CodeChunk`, `CreativeWork`, `Number`.

    Each node has a unique, immutable content identifier, `cid`, that is a hash of
    it's `json` content and other properties, generated at the time of creation.

    Each node is associated with a `project`. This is for authorization.
    Although the `cid` is a secret, project based authorization adds an additional
    layer of security e.g. in case of accidental leakage of a node URL.
    This field does not use cascading delete because node URLs
    should be permananent.

    Each node is created by an `app`. This string is primarily used when generating
    HTML representations of the node to provide links back to that app.

    A node is usually created within a `doc`. This is a URL that is primarily used
    when generating HTML representations of the bide to provide links back to the
    document.

    The `json` of the node is also immutable. It is returned to requests with
    `Accept: application/json` (if authorized).
    """

    class Meta:
        unique_together = (
            "project",
            "cid",
        )

    project = models.ForeignKey(
        Project,
        null=False,
        on_delete=models.DO_NOTHING,
        related_name="nodes",
        db_index=True,
        help_text="The project this node is associated with.",
    )

    app = models.TextField(
        null=True,
        blank=True,
        help_text="An identifier for the app that created the node.",
    )

    doc = models.URLField(
        null=True,
        blank=True,
        help_text="URL of the document within which the node was created.",
    )

    cid = models.TextField(
        db_index=True, help_text="The content identifier for the node."
    )

    json = models.TextField(help_text="The JSON content of node.")

    def get_absolute_url(self):
        return reverse("api-project-nodes-detail", kwargs={"cid": self.cid})
