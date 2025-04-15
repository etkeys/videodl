from os import path

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import App.constants as constants
from App.Config import Config


bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_message = "You must authenticate to access this page."
login_manager.login_message_category = "warning"
login_manager.login_view = "core.authenticate"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.debug = bool(int(app.config[constants.KEY_CONFIG_DEBUG_MODE]))
    app.name = app.config[constants.KEY_CONFIG_APP_NAME]

    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"]

    for key, val in app.config.items():
        if key.isupper():
            if isinstance(val, str) and "{{ APP_DIR }}" in val:
                app.config[key] = val.replace("{{ APP_DIR }}", app.root_path)
            else:
                app.config[key] = val

    if not path.isdir(app.config[constants.KEY_CONFIG_DIR_ARTIFACTS]):
        print(
            f"Directory '{app.config[constants.KEY_CONFIG_DIR_ARTIFACTS]}' does not exist. Exiting."
        )
        exit(4)

    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    constants.runtime_context.init_app(app)

    from App import utils

    app.jinja_env.globals.update(get_app_name=utils.get_app_name)
    app.jinja_env.globals.update(
        is_environment_development=utils.is_environment_development
    )

    app.jinja_env.filters["datetime_to_display"] = (
        utils.maybe_datetime_to_display_string
    )

    from App.routes import (
        admin_blueprint,
        core_blueprint,
        downloads_blueprint,
        todo_blueprint,
    )

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(core_blueprint)
    app.register_blueprint(downloads_blueprint)
    app.register_blueprint(todo_blueprint)

    return app
