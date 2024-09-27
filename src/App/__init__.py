import yaml
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_message = "You must authenticate to access this page."
login_manager.login_message_category = "warning"
login_manager.login_view = "core.authenticate"


def create_app(config_file: dict, config_section: str, exe_dir: str):
    app = Flask(__name__)

    config = read_yaml_config(config_file)[config_section]

    if "flask_debug" in config:
        app.debug = config["flask_debug"]
    if "flask_name" in config:
        app.name = config["flask_name"]

    for key, val in config.items():
        if key.isupper():
            if isinstance(val, str) and "{{ EXE_DIR }}" in val:
                app.config[key] = val.replace("{{ EXE_DIR }}", exe_dir)
            else:
                app.config[key] = val

    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from App import utils

    app.jinja_env.filters["datetime_to_display"] = (
        utils.maybe_datetime_to_display_string
    )

    from App.routes import core_blueprint, downloads_blueprint, todo_blueprint

    app.register_blueprint(core_blueprint)
    app.register_blueprint(downloads_blueprint)
    app.register_blueprint(todo_blueprint)

    return app


def read_yaml_config(config_file):
    with open(config_file) as f:
        y = yaml.safe_load(f)

    return y
