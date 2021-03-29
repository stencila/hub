import shortuuid
from django.db import models
from django.shortcuts import reverse
from meta.views import Meta
from stencila.schema.util import node_type as schema_node_type

from projects.models.projects import Project
from projects.models.sources import Source
from users.models import User, get_name


def generate_node_key():
    """
    Generate a unique, and very difficult to guess, key to access the node.
    """
    return shortuuid.ShortUUID().random(length=32)


# Applications known to create nodes
# For these provide further details in HTML views of nodes
APPS = {
    "api": ("API", "https://hub.stenci.la/api"),
    "encoda": ("Encoda", "https://github.com/stencila/encoda#readme"),
    "gsuita": (
        "Google Workspace",
        "https://workspace.google.com/marketplace/app/stencila/110435422451",
    ),
}


class Node(models.Model):
    """
    A Stencila Schema node.

    Could be any type of node e.g. a `CodeChunk`, `CreativeWork`, `Number` within
    some larger document, or a complete `Article` or `Review`.

    The `project` field allows the node to be associated with a project.
    This field is not required; this allows apps to create nodes in documents (e.g. GSuita)
    or to or to convert documents (e.g. Encoda) without having to associate them with a project.
    If the `project` is deleted then so are any associated nodes. This is primarily
    a housekeeping consideration to avoid many nodes associated with temporary projects.

    The `source` field allows the node to be associated with a project source.
    Storing this allows us to change the node's project if the source is moved
    from one project to another (e.g. from a temporary project to an existing project).
    Because a `source` is always associated with a project, to avoid conflicts (e.g.
    if a source is moved from one project to another), if `source` is set
    then `project` will be set to `None`.

    Each node is created by an `app`. This string is primarily used when generating
    HTML representations of the node to provide links back to that app.

    This `host` is a URL (often the URL of the `source`) which is primarily used
    when generating HTML representations of the node to provide links back to the
    document.

    The `json` of the node is also immutable. It is returned to requests with
    `Accept: application/json` (if authorized).

    Each node has a unique `key` generated at the time of creation. This
    is the only way to retreive a node. The `key` should be treated as a secret.
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
        on_delete=models.CASCADE,
        related_name="nodes",
        help_text="The project this node is associated with (if any).",
    )

    source = models.ForeignKey(
        Source,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="nodes",
        help_text="The source this node is associated with (if any).",
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

    key = models.CharField(
        unique=True,
        default=generate_node_key,
        max_length=64,
        help_text="A unique, and very difficult to guess, key to access this node if it is not public.",
    )

    json = models.JSONField(help_text="The JSON content of node.")

    def get_absolute_url(self):
        """Get the URL of this node."""
        return reverse("api-nodes-detail", kwargs={"key": self.key})

    def get_app(self):
        """Get name and URL of the creator app."""
        return APPS.get(self.app.lower(), (self.app, None))

    def get_meta(self) -> Meta:
        """Get the metadata to include in the head of the node's page."""
        json = self.json
        node_type = schema_node_type(json)
        if node_type in ("CodeChunk", "CodeExpression"):
            lang = json.get("programmingLanguage", "")
            kind = "code chunk" if node_type == "CodeChunk" else "code expression"
            title = f"{lang.title()} {kind}"
        elif node_type in ("MathBlock", "MathFragment"):
            lang = json.get("mathLanguage", "")
            kind = "math block" if node_type == "MathBlock" else "math fragment"
            title = f"{lang.title()} {kind}"
        else:
            title = node_type + " node"

        description = "Created"
        if self.creator:
            description += f" by { get_name(self.creator) }"

        app_name, app_url = self.get_app()
        if app_name:
            description += f" using { app_name }"

        if self.created:
            description += f" at { self.created } UTC"
        return Meta(object_type="article", title=title, description=description,)
