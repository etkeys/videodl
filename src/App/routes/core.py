from flask import Blueprint, redirect, url_for

core_blueprint = Blueprint("core", __name__)

@core_blueprint.get('/')
def route_to_initial_page():
    return redirect(url_for('queue.display_queue'))