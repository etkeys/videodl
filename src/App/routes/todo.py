from flask import abort, Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from App.forms.todo import DownloadItemDetailsForm
from App.models import DownloadItem, repo

todo_blueprint = Blueprint('todo', __name__, url_prefix='/todo')

@todo_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        # TODO Make safe characters in title

        ds_id = repo.get_todo_download_set(current_user.id).id

        new_item = DownloadItem(
            download_set_id=ds_id,
            url=form.url.data,
            title=form.title.data,
            audio_only=form.audio_only.data)

        try:
            repo.add_todo_download_item(current_user.id, new_item)
        except ValueError as e:
            abort(400, f"Could not add new item: {repr(e)}.")

        flash(f"Item added successfully.", category="success")
        return redirect(url_for('todo.display_todo'))
    else:
        return render_template('todo/add_edit_item.html', form=form, title="Add Item")

@todo_blueprint.get('/')
@login_required
def display_todo():
    items = repo.get_todo_download_items(current_user.id)
    items.sort(key=(lambda i: i.added_datetime))
    return render_template('todo/index.html', todo=items)

@todo_blueprint.get('/<id>/edit')
@login_required
def edit_item(id):
    item = repo.get_todo_download_item_by_id(current_user.id, id)
    if item is None:
        abort(404, description=f"Could not find item with Id of '{id}'.")

    form = DownloadItemDetailsForm()
    form.title.data = item.title
    form.audio_only.data = item.audio_only
    form.url.data = item.url

    return render_template(
        'todo/add_edit_item.html',
        form=form,
        title="Edit Item"
    )

@todo_blueprint.post('/<id>/edit')
@login_required
def edit_item_submit(id):
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        item = repo.get_todo_download_item_by_id(current_user.id, id)
        if item is None:
            abort(404, description=f"Could not find item with Id of '{id}'.")

        item.title = form.title.data
        item.audio_only = form.audio_only.data
        item.url = form.url.data

        flash('Item updated successfully.', category="success")
        return redirect(url_for('todo.display_todo'))

    else:
        return render_template(
            'todo/add_edit_item.html',
            form=form,
            title="Edit Item"
        )

@todo_blueprint.get('/delete')
@login_required
def confirm_delete_all():
    items = repo.get_todo_download_items(current_user.id)
    if len(items) < 1:
        return redirect(url_for('todo.display_todo'))

    return render_template("todo/delete_all.html", num_items=len(items))

@todo_blueprint.post('/delete')
@login_required
def delete_all():
    items = repo.get_todo_download_items(current_user.id)
    if len(items) > 0:
        repo.delete_todo_download_items(current_user.id)

    return redirect(url_for('todo.display_todo'))


@todo_blueprint.get('/<id>/delete')
@login_required
def confirm_delete_item(id):
    item = repo.get_todo_download_item_by_id(current_user.id, id)
    if item is None:
        abort(404, description=f"Could not find item with Id of '{id}'.")

    form = DownloadItemDetailsForm(True)
    form.title = item.title
    form.audio_only = item.audio_only
    form.url = item.url

    return render_template(
        'todo/delete_item.html',
        form=form
    )

@todo_blueprint.post('/<id>/delete')
@login_required
def delete_item(id):
    form = DownloadItemDetailsForm(True)
    if form.submit.data:
        repo.delete_todo_download_item_by_id(current_user.id, id)

        return redirect(url_for('todo.display_todo'))
    else:
        abort(400)

@todo_blueprint.get('/submit')
@login_required
def confirm_submit():
    items = repo.get_todo_download_items(current_user.id)
    if len(items) < 1:
        return redirect(url_for('todo.display_todo'))

    return render_template("todo/submit.html", num_items=len(items))

@todo_blueprint.post('/submit')
@login_required
def submit():
    repo.submit_todo_items(current_user.id)
    return redirect(url_for('core.root'))