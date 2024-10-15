from argparse import ArgumentParser
from datetime import timedelta
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

g_dir_artifacts = None
g_dir_logs = None


def get_arg_parser():
    parser = ArgumentParser(
        prog="Video DL Background Worker",
        description="A background script that performs the actual downloading of videos",
        add_help=True,
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

    return parser


def log(message: str, level: LogLevel = LogLevel.INFO, log_id: str = None):
    label = LogLevel.get_label(level)
    print(f"{label}: {message}")  # stdout, for journald
    if level >= LogLevel.INFO:
        with app.app_context():
            repo.add_worker_message(level, message)
    if log_id is not None:
        with open(path.join(g_dir_logs, f"{log_id}.log"), "a") as f:
            f.writelines(line + "\n" for line in [str(datetime_now()), message])


def do_download(
    item: DownloadItem,
    random_fail_download: bool,
    random_fail_finalize: bool,
):
    log(f"Downloading item '{item.id}'.")
    repo.update_download_item_status(item, DownloadItemStatus.DOWNLOADING)

    try:
        if repo.any_completed_items_with_url(item.download_set_id, item.url):
            raise RuntimeError("An already completed item has the same URL.")
        if repo.any_completed_items_with_file_name(item.download_set_id, item.file_name):
            raise RuntimeError("An already completed item has the same file name.")

        with TemporaryDirectory() as temp_dir:
            file_name = create_safe_file_name(item.title, item.audio_only)
            download_file = path.join(temp_dir, file_name)

            log("Executing download.", LogLevel.INFOLOW, log_id=item.id)

            if random_fail_download and choice([1, 2, 3, 4, 5]) < 3:
                raise Exception("Random fail event.")

            ret = subprocess.run(
                ["dd", "if=/dev/urandom", f"of={download_file}", "bs=1KB", "count=1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            log(ret.stdout.decode("utf-8"), LogLevel.INFOLOW, log_id=item.id)

            if ret.returncode == 0:
                log("Download complete. Moving to finalize.", LogLevel.INFOLOW)
                repo.update_download_item_status(item, DownloadItemStatus.FINALIZING)
            else:
                log("Download failed.", LogLevel.ERROR)
                repo.update_download_item_status(item, DownloadItemStatus.FAILED)
                return

            ds_art_dir = path.join(g_dir_artifacts, item.download_set_id)
            if not path.isdir(ds_art_dir):
                makedirs(ds_art_dir)

            log("Copying file to artifacts directory.", LogLevel.INFOLOW)
            copy2(download_file, ds_art_dir)

            if random_fail_finalize and choice([1, 2, 3, 4, 5]) < 3:
                raise Exception("Random fail event.")

            log("Complete. Done with item.", log_id=item.id)
            repo.update_download_item_status(item, DownloadItemStatus.COMPLETED)

    except Exception as ex:
        log(f"Error occurred during operation. {ex}", LogLevel.ERROR, log_id=item.id)
        log(format_exc(), LogLevel.DEBUG, log_id=item.id)
        repo.update_download_item_status(item, DownloadItemStatus.FAILED)


def pack_up_download_items(ds: DownloadSet):
    log(f"Packing up download set '{ds.id}'.", LogLevel.INFOLOW)
    ds_art_dir = path.join(g_dir_artifacts, ds.id)
    try:
        archive = make_archive(ds_art_dir, "zip", ds_art_dir)
        log(f"Download set completed. Archive created: '{archive}'")

        repo.update_download_set_status(ds, DownloadSetStatus.COMPLETED, archive)

    except Exception as ex:
        log(f"Error occurred during packing. {ex}", LogLevel.ERROR, log_id=ds.id)
        log(format_exc(), LogLevel.DEBUG, log_id=ds.id)
        repo.update_download_set_status(ds, DownloadSetStatus.PACKING_FAILED)


if __name__ == "__main__":
    args = get_arg_parser().parse_args()

    app = create_app()

    if not app.debug:
        args.random_fail_downloading = False
        args.random_fail_finalizing = False

    g_dir_artifacts = app.config[constants.KEY_CONFIG_DIR_ARTIFACTS]
    g_dir_logs = app.config[constants.KEY_CONFIG_DIR_LOGS]

    if not path.isdir(g_dir_artifacts):
        log(
            f"Directory '{g_dir_artifacts}' does not exist. Exiting.",
            LogLevel.ERROR,
        )
        exit(4)
    if not path.isdir(g_dir_logs):
        log(
            f"Directory '{g_dir_logs}' does not exist. Exiting.",
            LogLevel.ERROR,
        )
        exit(4)

    idle_wait_seconds = int(app.config[constants.KEY_CONFIG_WORKER_IDLE_WAIT_SECONDS])
    rate_limit_timeout_min = int(
        app.config[constants.KEY_CONFIG_WORKER_RATE_LIMIT_TIMEOUT_MIN_SECONDS]
    )
    rate_limit_timeout_max = int(
        app.config[constants.KEY_CONFIG_WORKER_RATE_LIMIT_TIMEOUT_MAX_SECONDS]
    )
    rate_limit_timeouts = range(rate_limit_timeout_min, rate_limit_timeout_max + 1)

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
                    timeout = idle_wait_seconds
                else:
                    log(f"Picking download set '{ds.id}' from queue.", LogLevel.INFOLOW)
                    repo.update_download_set_status(ds, DownloadSetStatus.PROCESSING)

            if not ds is None:
                log(f"Processing download set '{ds.id}'.")
                repo.reset_items_in_progress(ds.id)
                di = repo.get_oldest_queued_download_item(ds.id)

                if di is None:
                    log(
                        f"No items for download set '{ds.id}' left in queue.",
                        LogLevel.INFOLOW,
                    )
                    pack_up_download_items(ds)
                    timeout = idle_wait_seconds
                else:
                    do_download(
                        di,
                        args.random_fail_downloading,
                        args.random_fail_finalizing,
                    )
                    timeout = choice(rate_limit_timeouts)

        log(
            f"Sleeping for {timeout} seconds. Wake up at: {datetime_now() + timedelta(seconds=timeout)}."
        )
        sleep(timeout)
