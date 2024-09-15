from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'develop'
app.config['SESSION_PROTECTION'] = 'strong'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_message = 'You must authenticate to access this page.'
login_manager.login_message_category = 'warning'
login_manager.login_view = 'core.authenticate'

from App import utils

app.jinja_env.filters['datetime_to_display'] = utils.maybe_datetime_to_display_string

from App.routes import *

app.register_blueprint(core_blueprint)
app.register_blueprint(downloads_blueprint)
app.register_blueprint(todo_blueprint)