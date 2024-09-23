from flask import abort, Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from App.models import (
    DownloadItem,
    DownloadItemStatus,
    DownloadSet,
    DownloadSetStatus,
    repo,
)

downloads_blueprint = Blueprint("downloads", __name__, url_prefix="/downloads")


@downloads_blueprint.post("/<download_set_id>/add_failed_to_todo/<item_id>")
@login_required
def add_failed_item_to_todo(download_set_id, item_id):
    ds = repo.get_download_set_by_id(current_user.id, download_set_id)
    if ds is None:
        abort(404, f"Could not find Download Set with Id '{download_set_id}'.")
    if not ds.is_completed():
        abort(422, "Download Set is not completed.")

    item = repo.get_download_item_by_id(current_user.id, item_id)
    if item is None:
        abort(404, f"Could not find item with Id '{item_id}'.")
    if item.download_set_id != ds.id:
        abort(400, "Item is not part of Download Set.")
    if not item.is_failed():
        abort(422, "Item is not failed.")

    repo.copy_download_item_to_todo(current_user.id, item)
    flash("Item copied to To Do sucessfully.", category="success")
    return redirect(url_for("downloads.view_download_set", id=download_set_id))


@downloads_blueprint.post("/<download_set_id>/add_failed_to_todo")
@login_required
def add_all_failed_items_to_todo(download_set_id):
    for item in repo.get_download_items_failed(current_user.id, download_set_id):
        repo.copy_download_item_to_todo(current_user.id, item)
    flash("Items copied to To Do successfully.", category="success")
    return redirect(url_for("downloads.view_download_set", id=download_set_id))


@downloads_blueprint.get("/")
@login_required
def display_downloads():
    sets = repo.get_download_sets(current_user.id)
    sets.sort(reverse=True, key=(lambda s: s.created_datetime))
    return render_template("downloads/index.html", download_sets=sets)


@downloads_blueprint.get("/<id>/view")
@login_required
def view_download_set(id):
    ds = repo.get_download_set_by_id(current_user.id, id)
    if ds is None:
        abort(404, f"Could not find download set with Id '{id}'.")
    items = repo.get_download_items(current_user.id, id)
    items.sort(key=(lambda i: i.added_datetime))
    return render_template("downloads/view.html", download_set=ds, download_items=items)


@downloads_blueprint.app_template_filter("count_items_in_ds")
def count_items_in_download_set(ds: DownloadSet):
    return repo.count_items_in_download_set(current_user.id, ds.id)


@downloads_blueprint.app_template_filter("is_item_copied_to_todo")
def is_item_copied_to_todo(item: DownloadItem):
    return repo.is_item_copied_to_todo(current_user.id, item)
