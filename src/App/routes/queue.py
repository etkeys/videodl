from flask import abort, Blueprint, redirect, render_template, url_for

from App.forms.queue import DeleteDownloadItemsForm

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

@queue_blueprint.get('/')
def display_queue():
    return render_template('queue.html', queue=user_queue)

@queue_blueprint.get('/<id>/delete')
def confirm_delete_queue_item(id: int):
    try:
        item = next(i for i in user_queue if i['Id'] == int(id))

        form = DeleteDownloadItemsForm()
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
    form = DeleteDownloadItemsForm()
    if form.validate_on_submit():
        if form.submit_del.data:
            try:
                idx = next(i for i,x in enumerate(user_queue) if x['Id'] == int(id))
                del user_queue[idx]
            except StopIteration:
                abort(404, description=f"Could not find item with Id of '{id}'.")

        return redirect(url_for('queue.display_queue'))
    else:
        abort(400)

