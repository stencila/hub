"""
Create some nodes for each project.

The purpose of this is mainly to able to be able to preview
the HTML templates used for `Nodes` with real-ish data.

Generates the same nodes for every project (so you can
view them regardless of which test user you are logged in
as), with keys that are is easy to remember (the name of
the type).

Browse `/api/nodes/joe-private-project-codechunk.html` etc to preview the
templates with these data.
"""

from stencila.schema.types import CodeChunk, CodeExpression, MathBlock, MathFragment
from stencila.schema.json import object_encode

from projects.models import Project, Node

nodes = [
    CodeChunk(programmingLanguage="r", text="plot(mtcars)"),
    CodeExpression(programmingLanguage="js", text="x * y"),
    MathBlock(mathLanguage="tex", text="\\int\\limits_a^b x^2  \\mathrm{d} x"),
    MathFragment(mathLanguage="asciimath", text="2 pi r"),
]


def run(*args):
    for project in Project.objects.all():
        for node in nodes:
            Node.objects.get_or_create(
                project=project,
                key="{}-{}".format(project.name, node.__class__.__name__.lower()),
                app="gsuita",
                host="https://example.com/some-doc",
                json=object_encode(node),
            )
