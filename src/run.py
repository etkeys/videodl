from argparse import ArgumentParser
from os import path

from App import create_app, constants

parser = ArgumentParser(
            prog='Video DL',
            description='WebAPP for downloading videos from a URL.',
            add_help=True)

parser.add_argument('-c', '--config',
                    action='store',
                    default=constants.DEFAULT_CONFIG_FILE,
                    help=f"Path to the config file to load. Paths are relative to run.py. (default: {constants.DEFAULT_CONFIG_FILE})")


if __name__ == '__main__':
    args = parser.parse_args()

    app = create_app(config_file=args.config)

    app.config[constants.KEY_ARTIFACTS_DIR] = app.config[constants.KEY_ARTIFACTS_DIR].replace('{{ ROOT_PATH }}', app.root_path)
    if not path.isdir(app.config[constants.KEY_ARTIFACTS_DIR]):
        print(f"Directory '{app.config[constants.KEY_ARTIFACTS_DIR]}' does not exist. Exiting.")
        exit(4)

    app.run()