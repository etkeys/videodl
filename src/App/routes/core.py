from base64 import b64decode
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user

from App import bcrypt
from App.models import repo
from App.forms.core import AuthenticateForm

core_blueprint = Blueprint("core", __name__)


@core_blueprint.get("/")
@login_required
def root():
    if len(repo.get_todo_download_items(current_user.id)) > 0:
        return redirect(url_for("todo.display_todo"))
    return redirect(url_for("downloads.display_downloads"))


@core_blueprint.route("/auth", methods=["GET", "POST"])
def authenticate():
    if current_user.is_authenticated:
        return redirect(url_for("core.root"))

    form = AuthenticateForm()
    if form.validate_on_submit():
        credentials = b64decode(form.access_token.data).decode("utf-8").split("_")
        print(f"Credentials = {credentials}")
        if len(credentials) == 2:
            user = repo.get_user_by_name(credentials[1])
            if user and bcrypt.check_password_hash(user.pw_hash, credentials[0]):
                login_user(user, remember=False)
                next_page = request.args.get("next")
                return (
                    redirect(next_page) if next_page else redirect(url_for("core.root"))
                )
            else:
                flash(
                    "Login unsuccessful. Please check access token.",
                    category="error",
                )

    return render_template("core/auth.html", form=form)
