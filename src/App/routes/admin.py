from flask import abort, Blueprint, render_template
from flask_login import current_user, login_required

from App.models import repo
from App.utils import datetime_now
from App.utils.Exceptions import UnauthorizedError

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.get("worker_log")
@login_required
def view_worker_messages():
    try:
        messages = repo.get_worker_messages(current_user.id)
    except UnauthorizedError:
        abort(403, f"You do not have permissions for this request.")
    return render_template(
        "admin/worker_log.html", messages=messages, current_time=datetime_now()
    )
