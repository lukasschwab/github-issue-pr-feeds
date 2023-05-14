import json
from typing import List
from flask import Request, Response
import functions_framework
import requests
import jsonfeed
import markdown


def user_to_author(user: dict) -> jsonfeed.Author:
    return jsonfeed.Author(
        name=user.get("login"),
        url=user.get("html_url"),
        avatar=user.get("avatar_url")
    )


def to_item(issue: dict) -> jsonfeed.Item:
    return jsonfeed.Item(
        id=str(issue.get("number")),
        url=issue.get("html_url"),
        title=issue.get("title"),
        content_text=issue.get("body"),
        content_html=markdown.markdown(issue.get("body")),
        date_modified=issue.get("updated_at"),
        date_published=issue.get("created_at"),
        authors=[user_to_author(issue.get("user"))],
        tags=[label["name"] for label in issue.get("labels")]
    )


def issues(username, repository) -> List[jsonfeed.Item]:
    # Only open issues.
    resp = requests.get(f"https://api.github.com/repos/{username}/{repository}/issues")
    return [to_item(issue) for issue in resp.json()]
    

def pulls(username, repository) -> List[jsonfeed.Item]:
    # Only open pull requests.
    resp = requests.get(f"https://api.github.com/repos/{username}/{repository}/pulls")
    return [to_item(pull) for pull in resp.json()]


@functions_framework.http
def main(request: Request):
    print(json.dumps(dict(
        severity='INFO',
        message='Received request',
        request_url=request.url,
        trace_header=request.headers.get('X-Cloud-Trace-Context')
    )))
    username = request.args["username"]
    repository = request.args["repository"]
    feed = jsonfeed.Feed(
        title=f"GitHub Issues: {username}/{repository}",
        home_page_url=f"https://github.com/{username}/{repository}",
        feed_url=request.url,
        icon="https://github.githubassets.com/favicons/favicon.svg",
        items=pulls(username, repository)+issues(username, repository)
    )
    return Response(feed.to_json(), content_type='application/json; charset=utf-8')
