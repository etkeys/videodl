from flask import abort, Blueprint, flash, redirect, render_template, url_for, send_file
from flask_login import current_user, login_required

from App.models import (
    DownloadItemStatus,
    DownloadSetStatus,
    repo,
)
import App.utils as utils

status_color_map_di = {
    DownloadItemStatus.TODO: "status-color-todo",
    DownloadItemStatus.QUEUED: "status-color-todo",
    DownloadItemStatus.DOWNLOADING: "status-color-processing",
    DownloadItemStatus.FINALIZING: "status-color-processing",
    DownloadItemStatus.COMPLETED: "status-color-done",
    DownloadItemStatus.FAILED: "status-color-failed",
}

status_color_map_ds = {
    DownloadSetStatus.TODO: "status-color-todo",
    DownloadSetStatus.QUEUED: "status-color-todo",
    DownloadSetStatus.PROCESSING: "status-color-processing",
    DownloadSetStatus.COMPLETED: "status-color-done",
    DownloadSetStatus.PACKING_FAILED: "status-color-failed",
}

downloads_blueprint = Blueprint("downloads", __name__, url_prefix="/downloads")


@downloads_blueprint.post("/<download_set_id>/addAllItemsToTodo")
@login_required
def add_all_items_to_todo(download_set_id: str):
    ds = repo.get_download_set_by_id(current_user.id, download_set_id)
    if ds is None:
        abort(404, f"Could not find Download Set with Id '{download_set_id}'.")
    if not ds.is_packing_failed():
        abort(
            422,
            f"Can only perform action when status is '{DownloadSetStatus.PACKING_FAILED}'.",
        )

    try:
        count = repo.copy_download_set_items_to_todo(current_user.id, download_set_id)
        if count < 1:
            flash("No items were copied to To Do.", category="warning")
        else:
            flash("Items copied to To Do successfully.", category="success")
    except Exception as ex:
        flash(f"Failed to copy items to To Do. {ex}", category="error")

    return redirect(url_for("downloads.view_download_set", id=download_set_id))


@downloads_blueprint.post("/<download_set_id>/addFailedToTodo/<item_id>")
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
    if not item.is_failed():
        abort(422, "Item is not failed.")
    if item.download_set_id != ds.id:
        abort(400, "Item is not part of Download Set.")
    if not repo.is_item_copied_to_todo(current_user.id, item.id):
        repo.add_download_item(
            current_user.id,
            item.title,
            item.audio_only,
            item.url,
            item.file_name,
            item.id,
        )

    flash("Item copied to To Do sucessfully.", category="success")
    return redirect(url_for("downloads.view_download_set", id=download_set_id))


@downloads_blueprint.post("/<download_set_id>/addFailedToTodo")
@login_required
def add_all_failed_items_to_todo(download_set_id):
    ds = repo.get_download_set_by_id(current_user.id, download_set_id)
    if ds is None:
        abort(404, f"Could not find Download Set with Id '{download_set_id}'.")
    if not ds.is_completed():
        abort(422, "Download Set is not completed.")

    for item in repo.get_download_items_failed(current_user.id, download_set_id):
        if not repo.is_item_copied_to_todo(current_user.id, item.id):
            repo.add_download_item(
                current_user.id,
                item.title,
                item.audio_only,
                item.url,
                item.file_name,
                item.id,
            )

    flash("Items copied to To Do successfully.", category="success")
    return redirect(url_for("downloads.view_download_set", id=download_set_id))


@downloads_blueprint.get("/")
@login_required
def display_downloads():
    sets = repo.get_download_sets(current_user.id)
    return render_template("downloads/index.html", download_sets=sets)


@downloads_blueprint.get("/<download_set_id>/download")
@login_required
def download_archive(download_set_id: str):
    ds = repo.get_download_set_by_id(current_user.id, download_set_id)
    if ds is None:
        abort(404, "Could not find requested download set.")
    if not ds.is_completed():
        abort(422, "Requested download set is not completed.")
    if not utils.download_archive_exists(ds.archive_path):
        abort(404, "Could not find requested download set archive.")
    return send_file(ds.archive_path)


@downloads_blueprint.get("/<id>/view")
@login_required
def view_download_set(id):
    ds = repo.get_download_set_by_id(current_user.id, id, load_child_items_eagerly=True)
    if ds is None:
        abort(404, f"Could not find download set with Id '{id}'.")
    return render_template("downloads/view.html", download_set=ds)


@downloads_blueprint.app_template_filter("has_completed_items")
def download_set_has_completed_items(download_set_id: str):
    return 0 != repo.count_items_in_download_set_completed(
        current_user.id, download_set_id
    )


@downloads_blueprint.app_template_filter("has_failed_items")
def download_set_has_failed_items(download_set_id: str):
    return 0 != repo.count_items_in_download_set_failed(
        current_user.id, download_set_id
    )


@downloads_blueprint.app_template_filter("is_item_copied_to_todo")
def is_item_copied_to_todo(item_id: str):
    return repo.is_item_copied_to_todo(current_user.id, item_id)


@downloads_blueprint.app_template_filter("status_color_di")
def get_download_item_status_color(status: DownloadItemStatus):
    return status_color_map_di[status]


@downloads_blueprint.app_template_filter("status_color_ds")
def get_download_set_status_color(status: DownloadSetStatus):
    return status_color_map_ds[status]


@downloads_blueprint.app_context_processor
def blueprint_utilities():
    def count_items_in_download_set(user_id: str, download_set_id: str):
        return repo.count_items_in_download_set(user_id, download_set_id)

    return dict(count_items_in_ds=count_items_in_download_set)
