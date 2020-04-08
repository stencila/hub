import enum
import mimetypes
import typing
from os.path import splitext

DOCX_MIMETYPES = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    "application/vnd.ms-word.document.macroEnabled.12",
    "application/vnd.ms-word.template.macroEnabled.12",
)


class UnknownMimeTypeError(ValueError):
    pass


class ConversionFormat(typing.NamedTuple):
    format_id: str
    mimetypes: typing.Iterable[str]
    extensions: typing.List[str] = []

    @property
    def default_extension(self) -> str:
        """Get the default extension for the format."""
        return self.extensions[0] if len(self.extensions) else self.format_id

    @property
    def is_binary(self) -> bool:
        """Is the format be considered binary when determining the type of HTTP response."""
        return self.format_id not in ("html", "json", "jsonld", "md", "rmd", "xml")


class ConversionFormatId(enum.Enum):
    """
    List of formats we know how to work with.

    To add support for a conversion format:
    - Add it to the list below
    - Add a conversion for its mimetype to the `conversion_format_from_mimetype` function below
    - Check that its mimetype can be retrieved from its path using the `mimetype_from_path` function below (add support
      manually if necessary).
    """

    docx = ConversionFormat("docx", DOCX_MIMETYPES)
    gdoc = ConversionFormat("gdoc", ["application/vnd.google-apps.document"])
    html = ConversionFormat("html", ["text/html"])
    ipynb = ConversionFormat("ipynb", ["application/x-ipynb+json"])
    jats = ConversionFormat("jats", ["text/xml+jats"], ["jats.xml"])
    json = ConversionFormat("json", ["application/json"])
    jsonld = ConversionFormat("jsonld", ["application/ld+json"])
    md = ConversionFormat("md", ["text/markdown"])
    pdf = ConversionFormat("pdf", ["application/pdf"])
    rnb = ConversionFormat("rnb", ["text/html+rstudio"], ["nb.html"])
    rmd = ConversionFormat("rmd", ["text/rmarkdown"])
    xml = ConversionFormat("xml", ["application/xml"])

    @classmethod
    def from_id(cls, format_id: str) -> "ConversionFormatId":
        for f in cls:
            if f.value.format_id == format_id:
                return f

        raise ValueError("No such member with id {}".format(format_id))

    @classmethod
    def from_mimetype(cls, mimetype: str) -> "ConversionFormatId":
        for f in cls:
            if mimetype in f.value.mimetypes:
                return f

        raise ValueError("No such member with mimetype {}".format(mimetype))


def mimetype_from_path(path: str) -> typing.Optional[str]:
    """
    Get the mimetype of a file from its path.

    Takes the path instead of extension because some formats (e.g. JATS) have two extensions.
    """
    if path.lower().endswith(".jats.xml"):
        return "text/xml+jats"

    if path.lower().endswith(".nb.html"):
        return "text/html+rstudio"

    mimetype, encoding = mimetypes.guess_type(path, False)

    if not mimetype:
        name, ext = splitext(path)
        ext = ext.lower()

        if ext == ".md":
            return "text/markdown"

        if ext == ".rmd":
            return "text/rmarkdown"

        if ext == ".ipynb":
            return "application/x-ipynb+json"

        if ext == ".docx":
            return DOCX_MIMETYPES[0]

    return mimetype


def conversion_format_from_mimetype(mimetype: str) -> ConversionFormatId:
    try:
        return ConversionFormatId.from_mimetype(mimetype)
    except (UnknownMimeTypeError, ValueError):
        raise ConversionFormatError(
            "Unable to create ConversionFormatId from mimetype {}".format(mimetype)
        )


def conversion_format_from_path(path: str) -> ConversionFormatId:
    mimetype = mimetype_from_path(path)

    if not mimetype:
        raise UnknownMimeTypeError(
            "MIME type could not be determined for path: {}".format(path)
        )
    return conversion_format_from_mimetype(mimetype)


class ConversionFormatError(Exception):
    pass
