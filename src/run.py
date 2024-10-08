from argparse import ArgumentParser
from os import path

from App import create_app, constants
from App.utils import get_app_name

parser = ArgumentParser(
    prog="Video DL",
    description="WebAPP for downloading videos from a URL.",
    add_help=True,
)

parser.add_argument(
    "-c",
    "--config",
    action="store",
    default=constants.DEFAULT_CONFIG_FILE,
    help=f"Path to the config file to load. Paths are relative to run.py. (default: {constants.DEFAULT_CONFIG_FILE})",
)


if __name__ == "__main__":
    args = parser.parse_args()

    script_dir = path.dirname(path.abspath(__file__))

    app = create_app(args.config, "app_config", script_dir)

    if not path.isdir(app.config[constants.KEY_ARTIFACTS_DIR]):
        print(
            f"Directory '{app.config[constants.KEY_ARTIFACTS_DIR]}' does not exist. Exiting."
        )
        exit(4)

    app.jinja_env.globals.update(get_app_name=get_app_name)

    app.run()
