from argparse import ArgumentParser
from datetime import datetime, timezone, timedelta
from os import makedirs, path
from random import choice
import subprocess
from shutil import copy2, make_archive
from tempfile import TemporaryDirectory
from time import sleep
from traceback import format_exc

from App import constants, create_app
from App.models import (
    DownloadItem,
    DownloadItemStatus,
    DownloadSet,
    DownloadSetStatus,
    LogLevel,
)
from App.models.repo import worker_repo as repo
from App.utils import create_safe_file_name, datetime_now


parser = ArgumentParser(
    prog="Video DL Background Worker",
    description="A background script that performs the actual downloading of videos",
    add_help=True,
)

parser.add_argument(
    "-c",
    "--config",
    action="store",
    default=constants.DEFAULT_CONFIG_FILE,
    help=f"Path to the config file to load. Paths are relative to run.py. (default: {constants.DEFAULT_CONFIG_FILE})",
)

parser.add_argument(
    "--random-fail-downloading",
    action="store_true",
    help=f"Occasionally, downloading an item may fail (development only)",
)

parser.add_argument(
    "--random-fail-finalizing",
    action="store_true",
    help=f"Occasionally, finalizing an item may fail (development only)",
)


def log(message: str, level: LogLevel = LogLevel.INFO):
    label = LogLevel.get_label(level)
    print(f"{label}: {message}")  # stdout, for journald
    if level >= LogLevel.INFO:
        with app.app_context():
            repo.add_worker_message(level, message)


def do_download(
    item: DownloadItem,
    artifacts_dir,
    logs_dir,
    random_fail_download: bool,
    random_fail_finalize,
):
    log(f"Downloading item '{item.id}'.")
    repo.update_download_item_status(item, DownloadItemStatus.DOWNLOADING)

    try:
        with TemporaryDirectory() as temp_dir:
            file_name = create_safe_file_name(item.title, item.audio_only)
            download_file = path.join(temp_dir, file_name)

            log("Executing download.", LogLevel.INFOLOW)
            ret = subprocess.run(
                ["dd", "if=/dev/urandom", f"of={download_file}", "bs=1KB", "count=1"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

            # TODO write stderr and stdout to log file
            if random_fail_download and choice([1, 2, 3, 4, 5]) < 3:
                raise Exception("Random fail event.")

            if ret.returncode == 0:
                log("Download complete. Moving to finalize.", LogLevel.INFOLOW)
                repo.update_download_item_status(item, DownloadItemStatus.FINALIZING)
            else:
                log("Download failed.", LogLevel.ERROR)
                repo.update_download_item_status(item, DownloadItemStatus.FAILED)
                return

            ds_art_dir = path.join(artifacts_dir, item.download_set_id)
            if not path.isdir(ds_art_dir):
                makedirs(ds_art_dir)

            log("Copying file to artifacts directory.", LogLevel.INFOLOW)
            copy2(download_file, ds_art_dir)

            if random_fail_finalize and choice([1, 2, 3, 4, 5]) < 3:
                raise Exception("Random fail event.")

            log("Complete. Done with item.")
            repo.update_download_item_status(item, DownloadItemStatus.COMPLETED)

    except Exception as ex:
        log(f"Error occured during operation. {ex}")
        log(format_exc(ex), LogLevel.DEBUG)
        repo.update_download_item_status(item, DownloadItemStatus.FAILED)

        # TODO write exception to item log file


def pack_up_download_items(ds: DownloadSet, artifacts_dir, logs_dir):
    log(f"Packing up download set '{ds.id}'.", LogLevel.INFOLOW)
    ds_art_dir = path.join(artifacts_dir, ds.id)
    try:
        archive = make_archive(ds_art_dir, "zip", ds_art_dir)
        log(f"Download set completed. Archive created: '{archive}'")

        repo.update_download_set_status(ds, DownloadSetStatus.COMPLETED, archive)

    except Exception as ex:
        log(f"Error during packing. {ex}", LogLevel.ERROR)
        log(format_exc(ex))
        repo.update_download_set_status(ds, DownloadSetStatus.PACKING_FAILED)

        # TODO write error to set log file


if __name__ == "__main__":
    args = parser.parse_args()

    script_dir = path.dirname(path.abspath(__file__))

    app = create_app(args.config, "worker_config", script_dir)

    if not app.debug:
        args.random_fail_downloading = False
        args.random_fail_finalizing = False

    if not path.isdir(app.config[constants.KEY_ARTIFACTS_DIR]):
        log(
            f"Directory '{app.config[constants.KEY_ARTIFACTS_DIR]}' does not exist. Exiting.",
            LogLevel.ERROR,
        )
        exit(4)

    config = app.config
    default_timeout = config[constants.KEY_DEFAULT_WAIT_SECONDS]
    rate_limit_timeouts = range(35, 61)

    log("Entering main loop.", LogLevel.INFOLOW)
    while True:
        log("Starting work.")

        with app.app_context():
            ds = repo.get_processing_download_set()

            if ds is None:
                log('No download sets currently in "Processing".', LogLevel.INFOLOW)
                ds = repo.get_oldest_queued_download_set()

                if ds is None:
                    log('No download sets currently in "Queued".', LogLevel.INFOLOW)
                    log("Nothing to do.")
                    timeout = default_timeout
                else:
                    log(f"Picking download set '{ds.id}' from queue.", LogLevel.INFOLOW)
                    repo.update_download_set_status(ds, DownloadSetStatus.PROCESSING)

            if not ds is None:
                log(f"Processing download set '{ds.id}'.")
                di = repo.get_oldest_queued_download_item(ds.id)

                # TODO Reset items in FINALIZING or PROCESSING

                if di is None:
                    log(
                        f"No items for download set '{ds.id}' left in queue.",
                        LogLevel.INFOLOW,
                    )
                    pack_up_download_items(
                        ds,
                        config[constants.KEY_ARTIFACTS_DIR],
                        config[constants.KEY_LOGS_DIR],
                    )
                    timeout = default_timeout
                else:
                    do_download(
                        di,
                        config[constants.KEY_ARTIFACTS_DIR],
                        config[constants.KEY_LOGS_DIR],
                        args.random_fail_downloading,
                        args.random_fail_finalizing,
                    )
                    timeout = choice(rate_limit_timeouts)

        log(
            f"Sleeping for {timeout} seconds. Wake up at: {datetime_now() + timedelta(seconds=timeout)}."
        )
        sleep(timeout)
