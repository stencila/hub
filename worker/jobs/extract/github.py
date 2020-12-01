import json
import re
from typing import Callable, Dict, List, Optional, Tuple

from stencila.schema.types import Article, Comment, Person, Review

from jobs.convert import Convert
from util.github_api import github_client, github_user_as_person


def extract_github(
    source: Dict, filters: Dict = {}, secrets: Dict = {}, **kwargs
) -> Optional[Review]:
    """
    Extract a review from a GitHub pull request review.

    For details of the GitHub APIs see:

    - https://developer.github.com/v3/pulls/reviews/
    - https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html

    - https://developer.github.com/v3/pulls/comments/
    - https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html
    """
    repo = source.get("repo")
    assert repo, "GitHub repo is required"

    pr_number = filters.get("pr_number")
    assert pr_number, "A GitHub pull request number is required"
    pr_number = int(pr_number)

    review_id = filters.get("review_id")
    assert review_id, "A GitHub pull request review id is required"
    review_id = int(review_id)

    # Get the review and associated comments
    client = github_client(secrets.get("token"))
    pr = client.get_repo(repo).get_pull(pr_number)
    review = pr.get_review(review_id)
    comments = list(pr.get_single_review_comments(review_id))

    # Parse the body into an `Article`, augmenting properties
    # as needed
    article = parse_markdown(review.body)

    if not article.authors:
        article.authors = [github_user_as_person(review.user)]

    if not article.dateCreated:
        article.dateCreated = review.submitted_at.isoformat()

    return Review(
        **article.__dict__,
        comments=[parse_comment(comment) for comment in comments]
        if len(comments)
        else None,
    )


def parse_comment(comment) -> Comment:
    """
    Parse a pull request comment into a `Comment` node.
    """
    commentAspect = None
    path = comment.path
    if path:
        commentAspect = path
        position = comment.position
        if position:
            commentAspect += f"#L{position}"

    return Comment(
        authors=[github_user_as_person(comment.user)],
        dateCreated=comment.created_at,
        dateModified=comment.updated_at,
        commentAspect=commentAspect,
        content=[comment.body],
    )


def parse_markdown(content: str) -> Article:
    """
    Parse Markdown into an `Article` node.
    """
    data = json.loads(
        Convert().run(content, "-", {"from": "md", "to": "json"},).get("result")
    )
    del data["type"]
    return Article(**data)
