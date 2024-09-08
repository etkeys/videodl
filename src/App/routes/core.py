from flask import Blueprint, redirect, url_for

from App.models import repo

core_blueprint = Blueprint("core", __name__)

@core_blueprint.get('/')
def root():
    if len(repo.get_todo_download_items()) > 0:
        return redirect(url_for('todo.display_todo'))
    return redirect(url_for('downloads.display_downloads'))