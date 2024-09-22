
from argparse import ArgumentParser
from datetime import datetime, timezone, timedelta
from os import makedirs, path
from random import choice
import subprocess
from shutil import copy2
from tempfile import TemporaryDirectory
from time import sleep

from App import read_yaml_config, constants
from App.models import DownloadItem, DownloadItemStatus, DownloadSetStatus
from App.models.repo import worker_repo as repo
from App.utils import create_safe_file_name


parser = ArgumentParser(
            prog='Video DL Background Worker',
            description='A background script that performs the actual downloading of videos',
            add_help=True)

parser.add_argument('-c', '--config',
                    action='store',
                    default=constants.DEFAULT_CONFIG_FILE,
                    help=f"Path to the config file to load. Paths are relative to run.py. (default: {constants.DEFAULT_CONFIG_FILE})")

def main(config):
    default_timeout = config[constants.KEY_DEFAULT_WAIT_SECONDS]
    rate_limit_timeouts = range(35, 61)
    print("Entering main loop.")
    while True:
        print('Starting work.')

        ds = repo.get_processing_download_set()

        if ds is None:
            print('No download sets currently in "Processing".')
            ds = repo.get_oldest_queued_download_set()

            if ds is None:
                print ('No download sets currently in "Queued".')
                timeout = default_timeout
            else:
                print(f"Picking download set '{ds.id}' from queue.")
                repo.update_download_set_status(ds, DownloadSetStatus.PROCESSING)

        if not ds is None:
            print(f"Processing download set '{ds.id}'.")
            di = repo.get_oldest_queued_download_item(ds.id)

            if di is None:
                print(f"No items for download set '{ds.id}' in queue. Setting to \"Complete\".")
                repo.update_download_set_status(ds, DownloadSetStatus.COMPLETED)
                timeout = default_timeout
            else:
                do_download(di, config[constants.KEY_ARTIFACTS_DIR], config[constants.KEY_LOGS_DIR] )
                timeout = choice(rate_limit_timeouts)

        print(f"Sleeping for {timeout} seconds. Wake up at: {datetime.now(timezone.utc) + timedelta(seconds=timeout)}.")
        sleep(timeout)


def do_download(item: DownloadItem, artifacts_dir, logs_dir):
    print(f"Downloading item '{item.id}'.")
    repo.update_download_item_status(item, DownloadItemStatus.DOWNLOADING)

    try:
        with TemporaryDirectory() as temp_dir:
            file_name = create_safe_file_name(item.title, item.audio_only)
            download_file = path.join(temp_dir, file_name)

            print('Executing download.')
            ret = subprocess.run(
                [
                    'dd',
                    'if=/dev/urandom',
                    f"of={download_file}",
                    "bs=1KB",
                    "count=1"
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )

            # TODO write stderr and stdout to log file

            if ret.returncode == 0:
                print('Download complete. Moving to finalize.')
                repo.update_download_item_status(item, DownloadItemStatus.FINALIZING)
            else:
                print('Download failed.')
                repo.update_download_item_status(item, DownloadItemStatus.FAILED)
                return

            ds_art_dir = path.join(artifacts_dir, item.download_set_id)
            if not path.isdir(ds_art_dir):
                makedirs(ds_art_dir)

            print('Copying file to artifacts directory.')
            copy2(download_file, ds_art_dir)

            print('Finalizing complete. Done with item.')
            repo.update_download_item_status(item, DownloadItemStatus.COMPLETED)

    except Exception as ex:
        print('Error occured during operation.')
        print(ex)
        repo.update_download_set_status(item, DownloadItemStatus.FAILED)

        # TODO write exception to log file


if __name__ == '__main__':
    args = parser.parse_args()

    script_dir = path.dirname(path.abspath(__file__))

    config = read_yaml_config(config_file=args.config)
    config = config['worker_config']

    config[constants.KEY_ARTIFACTS_DIR] = config[constants.KEY_ARTIFACTS_DIR].replace('{{ ROOT_PATH }}', script_dir)
    config[constants.KEY_LOGS_DIR] = config[constants.KEY_LOGS_DIR].replace('{{ EXE_DIR }}', script_dir)

    if not path.isdir(config[constants.KEY_ARTIFACTS_DIR]):
        print(f"Directory '{config[constants.KEY_ARTIFACTS_DIR]}' does not exist. Exiting.")
        exit(4)

    main(config)
