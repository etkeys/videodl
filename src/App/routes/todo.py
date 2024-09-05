from flask import abort, Blueprint, flash, redirect, render_template, url_for

from App.forms.todo import DownloadItemDetailsForm
from App.models import DownloadItem, DownloadSet

todo_blueprint = Blueprint('todo', __name__, url_prefix='/todo')

user_download_set = DownloadSet()

user_todo = [
    DownloadItem(
        download_set_id=user_download_set.id,
        url='https://example.com/1',
        title='Video #1',
        audio_only=True),
    DownloadItem(
        download_set_id=user_download_set.id,
        url='https://example.com/2',
        title='Video #2'),
    DownloadItem(
        download_set_id=user_download_set.id,
        url='https://example.com/3',
        title='Video #3')
]

@todo_blueprint.route('/add', methods=['GET', 'POST'])
def add_item():
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        # TODO Make safe characters in title

        new_item = DownloadItem(
            download_set_id=user_download_set.id,
            url=form.url.data,
            title=form.title.data,
            audio_only=form.audio_only.data)
        user_todo.append(new_item)

        flash(f"Item added successfully.", category="success")
        return redirect(url_for('todo.display_todo'))
    else:
        return render_template('todo_add_edit_item.html', form=form, title="Add Item")

@todo_blueprint.get('/')
def display_todo():
    return render_template('todo.html', todo=user_todo)

@todo_blueprint.get('/<id>/edit')
def edit_item(id):
    try:
        item = next(i for i in user_todo if i.id == id)

        form = DownloadItemDetailsForm()
        form.title.data = item.title
        form.audio_only.data = item.audio_only
        form.url.data = item.url

        return render_template(
            'todo_add_edit_item.html',
            form=form,
            title="Edit Item"
        )
    except StopIteration:
        abort(404, description=f"Could not find item with Id of '{id}'.")

@todo_blueprint.post('/<id>/edit')
def edit_item_submit(id):
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        try:
            item = next(i for i in user_todo if i.id == id)

            item.title = form.title.data
            item.audio_only = form.audio_only.data
            item.url = form.url.data

            flash('Item updated successfully.', category="success")
            return redirect(url_for('todo.display_todo'))

        except StopIteration:
            abort(404, description=f"Could not find item with Id of '{id}'.")

    else:
        return render_template(
            'todo_add_edit_item.html',
            form=form,
            title="Edit Item"
        )

@todo_blueprint.get('/delete')
def confirm_delete_all():
    if len(user_todo) < 1:
        return redirect(url_for('todo.display_todo'))

    return render_template("todo_delete_all.html", num_items=len(user_todo))

@todo_blueprint.post('/delete')
def delete_all():
    if len(user_todo) > 0:
        user_todo.clear()

    return redirect(url_for('todo.display_todo'))


@todo_blueprint.get('/<id>/delete')
def confirm_delete_item(id):
    try:
        item = next(i for i in user_todo if i.id == id)

        form = DownloadItemDetailsForm(True)
        form.title = item.title
        form.audio_only = item.audio_only
        form.url = item.url

        return render_template(
            'todo_delete_item.html',
            form=form
        )
    except StopIteration:
        abort(404, description=f"Could not find item with Id of '{id}'.")

@todo_blueprint.post('/<id>/delete')
def delete_item(id):
    form = DownloadItemDetailsForm(True)
    if form.submit.data:
        try:
            idx = next(i for i,x in enumerate(user_todo) if x.id == id)
            del user_todo[idx]
        except StopIteration:
            abort(404, description=f"Could not find item with Id of '{id}'.")

        return redirect(url_for('todo.display_todo'))
    else:
        abort(400)

