from markdown import Markdown
from markdown.extensions.toc import TocExtension
from os import path
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user

from App.models import repo
from App.forms.core import AuthenticateForm
import App.utils.Authentication as app_auth

core_blueprint = Blueprint("core", __name__)


@core_blueprint.get("/")
@login_required
def root():
    if len(repo.get_todo_download_items(current_user.id)) > 0:
        return redirect(url_for("todo.display_todo"))
    return redirect(url_for("downloads.display_downloads"))


@core_blueprint.get("/about")
@login_required
def view_about():
    md = Markdown(extensions=[TocExtension(toc_depth="3-6")])
    with open(path.join("App", "static", "about.md")) as f:
        html = md.convert(f.read())

    return render_template("core/about.html", md_content=html)


@core_blueprint.route("/auth", methods=["GET", "POST"])
def authenticate():
    if current_user.is_authenticated:
        return redirect(url_for("core.root"))

    form = AuthenticateForm()
    if form.validate_on_submit():
        try:
            credentials = app_auth.decode_token(form.access_token.data)
        except Exception as ex:
            flash(f"Could not accept token. {ex}", category="error")
            return render_template("core/auth.html", form=form)

        user = repo.get_user_by_auth_id(credentials[0])
        if user and app_auth.check_password(user.pw_hash, credentials[1]):
            login_user(user, remember=False)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("core.root"))
        else:
            flash(
                "Login unsuccessful. Please check access token.",
                category="error",
            )

    return render_template("core/auth.html", form=form)
