from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'develop'

from App import utils

app.jinja_env.filters['datetime_to_display'] = utils.maybe_datetime_to_display_string

from App.routes import *

app.register_blueprint(core_blueprint)
app.register_blueprint(downloads_blueprint)
app.register_blueprint(todo_blueprint)