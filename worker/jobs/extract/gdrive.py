import json
import re
from typing import Callable, Dict, List, Optional

from googleapiclient.discovery import build
from stencila.schema.types import Comment, Person, Review

from jobs.convert import Convert
from util.gapis import gdrive_service


def extract_gdrive(
    source: Dict, filters: Optional[Dict] = {}, secrets: Optional[Dict] = {}, **kwargs
) -> Optional[Review]:
    """
    Extract a review from the comments for a Google document.
    """
    file_id = source.get("doc_id") or source.get("google_id")
    assert file_id, "A Google document or file id is required"
    assert secrets is not None, "Authentication tokens are required"

    return create_review(filter_comments(get_comments(file_id, secrets), filters))


def get_comments(file_id: str, secrets: Dict) -> List[Dict]:
    """
    Get all the comments on a document.
    """
    comments = []
    api = gdrive_service(secrets).comments()
    request = api.list(fileId=file_id, fields="*")
    while request is not None:
        response = request.execute()
        comments += response.get("comments", [])
        request = api.list_next(request, response)
    return comments


def filter_comments(comments: List[Dict], filters: Optional[Dict] = {}) -> List[Dict]:
    """
    Filter a list of comments.
    """
    if filters is None:
        return comments

    filtered = []
    for comment in comments:
        ok = True
        for key, regex in filters.items():
            if key == "name":
                if not re.match(regex, comment.get("author", {}).get("displayName")):
                    ok = False
        if ok:
            filtered.append(comment)

    return filtered


def create_review(comments: List[Dict]) -> Optional[Review]:
    """
    Create a`Review` from a list of comments.
    """
    if len(comments) == 0:
        return None

    # Find the main comment in the review
    main = None
    rest = []
    for comment in comments:
        text = comment.get("content", "")
        if main is None and re.match(r"^#\sReview", text):
            main = comment
        else:
            rest.append(comment)
    if main is None:
        main = comments[0]

    # Parse the main comment into the review
    review = parse_comment(main, parse_markdown=True)
    if review is None:
        return None

    # Convert the `Comment` into a `Review`
    review_properties = review.__dict__
    if "commentAspect" in review_properties:
        del review_properties["commentAspect"]

    # Parse the rest into its comments
    review_comments = list(filter(lambda x: x is not None, map(parse_comment, rest)))

    return Review(**review_properties, comments=review_comments,)


def parse_comment(data: Dict, parse_markdown=False) -> Optional[Comment]:
    """
    Parse a dictionary of comment data into a `Comment` instance.

    For a list of comment properties available see
    https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.comments.html#list
    """
    content = data.get("content", "").strip()
    if not content:
        return None

    if parse_markdown:
        article = json.loads(
            Convert().run(content, "-", {"from": "md", "to": "json"},).get("result")
        )
        if not article:
            raise RuntimeError("Failed to convert review body from Markdown")
        del article["type"]
        comment = Comment(**article)
    else:
        comment = Comment(content=[content])

    author = data.get("author")
    if not comment.authors and author:
        name = author.get("displayName")
        email = author.get("emailAddress")
        comment.authors = [Person(name=name, emails=[email] if email else None)]

    dateCreated = data.get("createdTime")
    if not comment.dateCreated and dateCreated:
        comment.dateCreated = dateCreated

    dateModified = data.get("modifiedTime")
    if not comment.dateModified and dateModified:
        comment.dateModified = dateModified

    commentAspect = data.get("quotedFileContent", {}).get("value")
    if not comment.commentAspect and commentAspect:
        comment.commentAspect = commentAspect

    comments = data.get("replies", [])
    if len(comments) > 0:
        comment.comments = list(map(parse_comment, comments))

    return comment
