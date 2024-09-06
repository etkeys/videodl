from flask import Blueprint, redirect, url_for

core_blueprint = Blueprint("core", __name__)

@core_blueprint.get('/')
def root():
    return redirect(url_for('todo.display_todo'))