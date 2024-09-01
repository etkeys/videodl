from flask import Blueprint, render_template

queue_blueprint = Blueprint('queue', __name__, url_prefix='/queue')

user_queue = [
        { 'Url': 'https://example.com/1',
         'Title': 'Video #1',
         'AudioOnly': True},
        { 'Url': 'https://example.com/2',
         'Title': 'Video #2',
         'AudioOnly': False},
        { 'Url': 'https://example.com/3',
         'Title': 'Video #3',
         'AudioOnly': False}
]

@queue_blueprint.route('/')
def queue():
    return render_template('queue.html', queue=user_queue)