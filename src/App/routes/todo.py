from flask import abort, Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from App.forms.todo import DownloadItemDetailsForm
from App.models import repo

todo_blueprint = Blueprint("todo", __name__, url_prefix="/todo")


@todo_blueprint.route("/add", methods=["GET", "POST"])
@login_required
def add_item():
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        try:
            repo.add_download_item(
                current_user.id, form.title.data, form.audio_only.data, form.url.data
            )
            flash(f"Item added successfully.", category="success")
            return redirect(url_for("todo.display_todo"))
        except Exception as ex:
            flash(f"Item cannot be added. {str(ex)}", category="error")
            return render_template(
                "todo/add_edit_item.html", form=form, title="Add Item"
            )
    else:
        return render_template("todo/add_edit_item.html", form=form, title="Add Item")


@todo_blueprint.get("/")
@login_required
def display_todo():
    items = repo.get_todo_download_items(current_user.id)
    return render_template("todo/index.html", todo=items)


@todo_blueprint.get("/<id>/edit")
@login_required
def edit_item(id):
    item = repo.get_todo_download_item_by_id(current_user.id, id)
    if item is None:
        abort(404, description=f"Could not find item with Id of '{id}'.")

    form = DownloadItemDetailsForm()
    form.title.data = item.title
    form.audio_only.data = item.audio_only
    form.url.data = item.url

    return render_template("todo/add_edit_item.html", form=form, title="Edit Item")


@todo_blueprint.post("/<id>/edit")
@login_required
def edit_item_submit(id):
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        item = repo.get_todo_download_item_by_id(current_user.id, id)
        if item is None:
            abort(404, description=f"Could not find item with Id of '{id}'.")

        try:
            repo.update_item(
                current_user.id,
                id,
                title=form.title.data,
                audio_only=form.audio_only.data,
                url=form.url.data,
            )
            flash("Item updated successfully.", category="success")
            return redirect(url_for("todo.display_todo"))
        except Exception as ex:
            flash(f"Item cannot be updated. {str(ex)}", category="error")
            return render_template(
                "todo/add_edit_item.html", form=form, title="Edit Item"
            )
    else:
        return render_template("todo/add_edit_item.html", form=form, title="Edit Item")


@todo_blueprint.get("/delete")
@login_required
def confirm_delete_all():
    items = repo.get_todo_download_items(current_user.id)
    if len(items) < 1:
        return redirect(url_for("todo.display_todo"))

    return render_template("todo/delete_all.html", num_items=len(items))


@todo_blueprint.post("/delete")
@login_required
def delete_all():
    items = repo.get_todo_download_items(current_user.id)
    if len(items) > 0:
        repo.delete_todo_download_items(current_user.id)

    return redirect(url_for("todo.display_todo"))


@todo_blueprint.get("/<id>/delete")
@login_required
def confirm_delete_item(id):
    item = repo.get_todo_download_item_by_id(current_user.id, id)
    if item is None:
        abort(404, description=f"Could not find item with Id of '{id}'.")

    form = DownloadItemDetailsForm(True)
    form.title = item.title
    form.audio_only = item.audio_only
    form.url = item.url

    return render_template("todo/delete_item.html", form=form)


@todo_blueprint.post("/<id>/delete")
@login_required
def delete_item(id):
    form = DownloadItemDetailsForm(True)
    if form.submit.data:
        repo.delete_todo_download_item_by_id(current_user.id, id)

        return redirect(url_for("todo.display_todo"))
    else:
        abort(400)


@todo_blueprint.get("/submit")
@login_required
def confirm_submit():
    # TODO need to add a count function instead getting all the things
    items = repo.get_todo_download_items(current_user.id)
    if len(items) < 1:
        return redirect(url_for("todo.display_todo"))

    return render_template("todo/submit.html", num_items=len(items))


@todo_blueprint.post("/submit")
@login_required
def submit():
    repo.submit_todo_items(current_user.id)
    return redirect(url_for("core.root"))
