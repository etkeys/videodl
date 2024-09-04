from flask import abort, Blueprint, flash, redirect, render_template, url_for

from App.forms.queue import DownloadItemDetailsForm

queue_blueprint = Blueprint('queue', __name__, url_prefix='/queue')

user_queue = [
        { 'Id': 1,
         'Url': 'https://example.com/1',
         'Title': 'Video #1',
         'AudioOnly': True},
        { 'Id': 10,
         'Url': 'https://example.com/2',
         'Title': 'Video #2',
         'AudioOnly': False},
        { 'Id': 100,
         'Url': 'https://example.com/3',
         'Title': 'Video #3',
         'AudioOnly': False}
]

@queue_blueprint.route('/add', methods=['GET', 'POST'])
def add_item():
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        next_id = max([i['Id'] for i in user_queue]) * 10

        # TODO Make safe characters in title

        new_item = {
            'Id': next_id,
            'Title': form.title.data,
            'AudioOnly': form.audio_only.data,
            'Url': form.url.data,
        }
        user_queue.append(new_item)
        flash(f"Item '{new_item['Title']}' added successfully.", category="success")
        return redirect(url_for('queue.display_queue'))
    else:
        return render_template('queue_add_edit_item.html', form=form, title="Add Item")

@queue_blueprint.get('/')
def display_queue():
    return render_template('queue.html', queue=user_queue)

@queue_blueprint.get('/<id>/edit')
def edit_item(id: int):
    try:
        item = next(i for i in user_queue if i['Id'] == int(id))

        form = DownloadItemDetailsForm()
        form.title.data = item['Title']
        form.audio_only.data = item['AudioOnly']
        form.url.data = item['Url']

        return render_template(
            'queue_add_edit_item.html',
            form=form,
            title="Edit Item"
        )
    except StopIteration:
        abort(404, description=f"Could not find item with Id of '{id}'.")

@queue_blueprint.post('/<id>/edit')
def edit_item_submit(id: int):
    form = DownloadItemDetailsForm()
    if form.validate_on_submit():
        try:
            item = next(i for i in user_queue if i['Id'] == int(id))

            item['Title'] = form.title.data
            item['AudioOnly'] = form.audio_only.data
            item['Url'] = form.url.data

            flash('Item updated successfully.', category="success")
            return redirect(url_for('queue.display_queue'))

        except StopIteration:
            abort(404, description=f"Could not find item with Id of '{id}'.")

    else:
        return render_template(
            'queue_add_edit_item.html',
            form=form,
            title="Edit Item"
        )

@queue_blueprint.get('/<id>/delete')
def confirm_delete_queue_item(id: int):
    try:
        item = next(i for i in user_queue if i['Id'] == int(id))

        form = DownloadItemDetailsForm(True)
        form.title = item['Title']
        form.audio_only = item['AudioOnly']
        form.url = item['Url']

        return render_template(
            'queue_delete_item.html',
            form=form
        )
    except StopIteration:
        abort(404, description=f"Could not find item with Id of '{id}'.")

@queue_blueprint.post('/<id>/delete')
def delete_queue_item(id: int):
    form = DownloadItemDetailsForm(True)
    if form.submit.data:
        try:
            idx = next(i for i,x in enumerate(user_queue) if x['Id'] == int(id))
            del user_queue[idx]
        except StopIteration:
            abort(404, description=f"Could not find item with Id of '{id}'.")

        return redirect(url_for('queue.display_queue'))
    else:
        abort(400)

