from flask import abort, Blueprint, render_template
from flask_login import current_user, login_required

from App.models import repo
from App.utils import datetime_now
from App.utils.Exceptions import UnauthorizedError

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


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


@admin_blueprint.get("worker_log")
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
