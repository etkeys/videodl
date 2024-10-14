from base64 import b64encode
from flask import abort, Blueprint, flash, redirect, render_template, Response, url_for
from flask_login import current_user, login_required

from App import bcrypt
from App.forms.admin import AddEditUserForm
from App.models import repo
from App.utils import datetime_now, get_log_file_contents, new_id
from App.utils.Exceptions import UnauthorizedError
import App.utils.Authentication as app_auth

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.route("users/add", methods=["GET", "POST"])
@login_required
def add_user():
    _abort_403_if_not_admin()
    form = AddEditUserForm()
    if form.validate_on_submit():
        try:
            auth_id, pw_hash, token = app_auth.create_new_credentials()

            repo.add_user(
                name=form.name.data,
                email=form.email.data,
                is_admin=form.is_admin.data,
                pw_hash=pw_hash,
                auth_id=auth_id,
            )

            flash("User added successfully.", category="success")
            return render_template(
                "admin/user_new_token.html",
                user_name=form.name.data,
                user_email=form.email.data,
                access_token=token,
                for_add=True,
            )

        except Exception as ex:
            flash(f"Unable to add user. {ex}", category="error")
            return render_template("admin/add_edit_user.html", form=form)

    else:
        return render_template("admin/add_edit_user.html", form=form)


@admin_blueprint.get("users/<user_id>/edit")
@login_required
def edit_user(user_id: str):
    _abort_403_if_not_admin()
    user = repo.get_user_by_id(user_id)
    if user is None:
        abort(404, "Could not find requested user.")
    form = AddEditUserForm(True)
    form.name.data = user.name
    form.email.data = user.email
    form.is_admin.data = user.is_admin

    return render_template("admin/add_edit_user.html", form=form)


@admin_blueprint.post("users/<user_id>/edit")
@login_required
def edit_user_submit(user_id: str):
    _abort_403_if_not_admin()
    form = AddEditUserForm(True)
    if form.validate_on_submit():
        try:
            repo.update_user(
                user_id,
                name=form.name.data,
                email=form.email.data,
                is_admin=form.is_admin.data,
            )
        except Exception as ex:
            flash(f"Cannot save changes. {ex}", category="error")
            return render_template("admin/add_edit_user.html", form=form)

        flash(f"User updated successfully.", category="success")
        return redirect(url_for("admin.view_users"))

    return render_template("admin/add_edit_user.html", form=form)


@admin_blueprint.post("users/<user_id>/reset")
@login_required
def reset_user(user_id: str):
    _abort_403_if_not_admin()
    user = repo.get_user_by_id(user_id)
    if user.id == current_user.id:
        abort(422, "Cannot reset yourself")

    new_auth_id, new_pw_hash, new_access_token = app_auth.create_new_credentials()

    try:
        repo.update_user(user_id, auth_id=new_auth_id, pw_hash=new_pw_hash)
        return render_template(
            "admin/user_new_token.html",
            user_name=user.name,
            user_email=user.email,
            access_token=new_access_token,
            for_add=False,
        )
    except Exception as ex:
        flash(f"Unable to reset user. {ex}")
        return redirect(url_for("admin.view_users"))


@admin_blueprint.get("users/<user_id>/downloads/<download_set_id>/")
@login_required
def view_download_set(user_id: str, download_set_id: str):
    _abort_403_if_not_admin()
    ds = repo.get_download_set_by_id(
        user_id, download_set_id, load_child_items_eagerly=True
    )
    if ds is None:
        abort(404, f"Could not find download set with Id '{id}'.")
    return render_template("downloads/view.html", download_set=ds, admin_view=True)


@admin_blueprint.get("logs/<log_id>")
@login_required
def view_log(log_id: str):
    _abort_403_if_not_admin()
    content = get_log_file_contents(log_id)
    if content is None:
        return Response(status=204)
    return Response(content, mimetype="text/plain")


@admin_blueprint.get("users/<user_id>/downloads")
@login_required
def view_user_downloads(user_id: str):
    _abort_403_if_not_admin()
    sets = repo.get_download_sets(user_id)
    return render_template("downloads/index.html", download_sets=sets, admin_view=True)


@admin_blueprint.get("users")
@login_required
def view_users():
    _abort_403_if_not_admin()
    try:
        users = repo.get_users(current_user.id)
    except UnauthorizedError:
        abort(403, f"You do not have permissions for this request.")
    return render_template("admin/users.html", users=users)


@admin_blueprint.get("workerLog")
@login_required
def view_worker_messages():
    _abort_403_if_not_admin()
    try:
        messages = repo.get_worker_messages(current_user.id)
    except UnauthorizedError:
        abort(403, f"You do not have permissions for this request.")
    return render_template(
        "admin/worker_log.html", messages=messages, current_time=datetime_now()
    )


@admin_blueprint.app_context_processor
def blueprint_utilities():
    def count_download_sets(user_id: str):
        return repo.count_download_sets(user_id)

    def count_items_in_download_set(user_id: str, download_set_id: str):
        return repo.count_items_in_download_set(user_id, download_set_id)

    return dict(
        count_download_sets=count_download_sets,
        count_items_in_download_set=count_items_in_download_set,
    )


def _abort_403_if_not_admin():
    if not current_user.is_admin:
        abort(403, f"You do not have permissions for this request.")
