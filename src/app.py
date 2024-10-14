from os import path

from App import create_app, constants
from App.utils import get_app_name


if __name__ == "__main__":
    app = create_app()

    if not path.isdir(app.config[constants.KEY_CONFIG_DIR_ARTIFACTS]):
        print(
            f"Directory '{app.config[constants.KEY_CONFIG_DIR_ARTIFACTS]}' does not exist. Exiting."
        )
        exit(4)

    app.jinja_env.globals.update(get_app_name=get_app_name)

    app.run()
