from flask import Blueprint, render_template, request

from startaste.dashboard.services import (
    get_overview,
    get_hn_stories,
    get_hn_comments,
    get_github_stars,
)

bp = Blueprint("dashboard", __name__, template_folder="templates", static_folder="static")


@bp.route("/")
def index():
    data = get_overview()
    return render_template("index.html", **data)


@bp.route("/hn")
def hn():
    page = request.args.get("page", 1, type=int)
    data = get_hn_stories(page=page)
    return render_template("hn.html", tab="stories", **data)


@bp.route("/hn/comments")
def hn_comments():
    page = request.args.get("page", 1, type=int)
    data = get_hn_comments(page=page)
    return render_template("hn.html", tab="comments", **data)


@bp.route("/github")
def github():
    page = request.args.get("page", 1, type=int)
    data = get_github_stars(page=page)
    return render_template("github.html", **data)
