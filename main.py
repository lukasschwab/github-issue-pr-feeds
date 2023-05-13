import json
from flask import Request, Response
import functions_framework
import requests
import jsonfeed
import markdown


def user_to_author(user: dict) -> jsonfeed.Author:
    return jsonfeed.Author(
        name=user.get("login"),
        url=user.get("url"),
        avatar=user.get("avatar_url")
    )


def item(issue: dict) -> jsonfeed.Item:
    return jsonfeed.Item(
        id=issue.get("number"),
        url=issue.get("url"),
        title=issue.get("title"),
        content_text=issue.get("body"),
        content_html=markdown.markdown(issue.get("body")),
        date_modified=issue.get("updated_at"),
        date_published=issue.get("created_at"),
        authors=[user_to_author(issue.get("user"))],
        tags=[label["name"] for label in issue.get("labels")]
    )


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
    resp = requests.get(f"https://api.github.com/repos/{username}/{repository}/issues")
    feed = jsonfeed.Feed(
        title=f"GitHub Issues: {username}/{repository}",
        home_page_url=f"https://github.com/{username}/{repository}",
        feed_url=request.url,
        icon="https://github.githubassets.com/favicons/favicon.svg",
        items=[item(issue) for issue in resp.json()]
    )
    return Response(feed.to_json(), content_type='application/json; charset=utf-8')
