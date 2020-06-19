import enum


@enum.unique
class ProviderId(enum.Enum):
    """
    An enumeration of the social account providers used by the Hub.
    """

    github = "github"
    google = "google"
    orcid = "orcid"
    twitter = "twitter"
