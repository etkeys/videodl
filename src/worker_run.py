from argparse import ArgumentParser
from datetime import datetime, timedelta
from os import makedirs, path, remove, walk
from random import choice
import subprocess
from shutil import make_archive, move, rmtree
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

g_version_message = """
Video DL Background Worker
Version: {{ version_string }}
Build Date: {{ build_date_string }}
"""
g_dir_artifacts = None
g_dir_logs = None
g_simulate = False
g_downloader_app = "yt-dlp"

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

    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Toggles between actually performing download or creating fake files. In development mode, passing this flag will have the opposite effect.",
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
        if repo.any_completed_items_with_file_name(
            item.download_set_id, item.file_name
        ):
            raise RuntimeError("An already completed item has the same file name.")

        with TemporaryDirectory() as temp_dir:
            download_file = path.join(temp_dir, item.file_name)

            log("Executing download.", LogLevel.INFOLOW, log_id=item.id)

            if random_fail_download and choice([1, 2, 3, 4, 5]) < 3:
                raise Exception("Random fail event.")

            if g_simulate:
                run_args = [
                    "dd",
                    "if=/dev/urandom",
                    f"of={download_file}",
                    "bs=1KB",
                    "count=1",
                ]
            else:
                run_args = [
                    g_downloader_app,
                    "--verbose",
                    "--restrict-filename",
                    "--paths",
                    temp_dir,
                ]
                if item.audio_only:
                    run_args += ["--extract-audio", "--audio-format", "mp3"]
                run_args += [item.url, "--exec", f"cp {{}} {download_file}"]

            ret = subprocess.run(
                run_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            log(ret.stdout.decode("utf-8"), LogLevel.DEBUG, log_id=item.id)

            if ret.returncode == 0:
                log("Download complete. Moving to finalize.", LogLevel.INFOLOW)
                repo.update_download_item_status(item, DownloadItemStatus.FINALIZING)
            else:
                log("Download failed.", LogLevel.ERROR)
                repo.update_download_item_status(item, DownloadItemStatus.FAILED)
                return

            log(
                "Waiting 2 seconds for file system to catch up.",
                LogLevel.DEBUG,
                log_id=item.id,
            )
            sleep(2)

            ds_art_dir = path.join(g_dir_artifacts, item.download_set_id)
            if not path.isdir(ds_art_dir):
                makedirs(ds_art_dir)

            log("Copying file to artifacts directory.", LogLevel.INFOLOW)
            move(download_file, ds_art_dir)

            if random_fail_finalize and choice([1, 2, 3, 4, 5]) < 3:
                raise Exception("Random fail event.")

            log("Complete. Done with item.", log_id=item.id)
            repo.update_download_item_status(item, DownloadItemStatus.COMPLETED)

    except Exception as ex:
        log(f"Error occurred during operation. {ex}", LogLevel.ERROR, log_id=item.id)
        log(format_exc(), LogLevel.DEBUG, log_id=item.id)
        repo.update_download_item_status(item, DownloadItemStatus.FAILED)

def do_prune(prune_time: datetime):
    log(f"Pruning data older than {prune_time}.", LogLevel.INFO)
    prune_logs(prune_time)
    prune_artifacts(prune_time)
    repo.prune_download_sets(prune_time)

def ignore_file(file: str) -> bool:
    if file.startswith("."):
        return True
    return False

def prune_artifacts(prune_time: datetime):
    log("Pruning artifacts.", LogLevel.INFO)
    prune_time_ts = prune_time.timestamp()
    for root, dirs, files in walk(g_dir_artifacts, topdown=False):
        for file in files:
            if ignore_file(file):
                log(f"Ignoring file '{file}'.", LogLevel.INFOLOW)
                continue
            file_path = path.join(root, file)
            try:
                if path.isfile(file_path):
                    file_time_ts = path.getmtime(file_path)
                    if file_time_ts < prune_time_ts:
                        log(f"Deleting artifact file '{file}'.", LogLevel.INFOLOW)
                        remove(file_path)
            except Exception as ex:
                log(f"Error deleting file '{file}': {ex}", LogLevel.ERROR)
                log(format_exc(), LogLevel.DEBUG)
                continue

        for dir in dirs:
            dir_path = path.join(root, dir)
            try:
                if path.isdir(dir_path):
                    dir_time_ts = path.getmtime(dir_path)
                    if dir_time_ts < prune_time_ts:
                        log(f"Deleting artifact directory '{dir}'.", LogLevel.INFOLOW)
                        rmtree(dir_path)
            except Exception as ex:
                log(f"Error deleting directory '{dir}': {ex}", LogLevel.ERROR)
                log(format_exc(), LogLevel.DEBUG)
                continue

def prune_logs(prune_time: datetime):
    log("Pruning logs.", LogLevel.INFO)
    prune_time_ts = prune_time.timestamp()
    for root, _, files in walk(g_dir_logs, topdown=False):
        for file in files:
            if ignore_file(file):
                log(f"Ignoring file '{file}'.", LogLevel.INFOLOW)
                continue
            file_path = path.join(g_dir_logs, file)
            try:
                if path.isfile(file_path):
                    file_time_ts = path.getmtime(file_path)
                    if file_time_ts < prune_time_ts:
                        log(f"Deleting log file '{file}'.", LogLevel.INFOLOW)
                        remove(file_path)
            except Exception as ex:
                log(f"Error deleting log file '{file}': {ex}", LogLevel.ERROR)
                log(format_exc(), LogLevel.DEBUG)
                continue

def get_download_set() -> DownloadSet:
    ds = repo.get_processing_download_set()
    if ds is None:
        ds = repo.get_oldest_queued_download_set()

    if ds is None:
        log("No download sets currently in 'Processing' or 'Queued'.", LogLevel.INFOLOW)
        return None

    log(f"Picked download set '{ds.id}' for processing.", LogLevel.INFOLOW)
    repo.update_download_set_status(ds, DownloadSetStatus.PROCESSING)
    return ds

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
    print(g_version_message)

    args = get_arg_parser().parse_args()

    app = create_app()

    if not app.debug:
        args.random_fail_downloading = False
        args.random_fail_finalizing = False

    g_dir_artifacts = app.config[constants.KEY_CONFIG_DIR_ARTIFACTS]
    g_dir_logs = app.config[constants.KEY_CONFIG_DIR_LOGS]
    if app.debug:
        g_simulate = not args.simulate
    else:
        g_simulate = args.simulate

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

    idle_wait_seconds_min = int(app.config[constants.KEY_CONFIG_WORKER_MIN_IDLE_TIMEOUT_SECONDS])
    idle_wait_seconds_max = int(app.config[constants.KEY_CONFIG_WORKER_MAX_IDLE_TIMEOUT_SECONDS])
    idle_wait_seconds = range(idle_wait_seconds_min, idle_wait_seconds_max + 1)
    prune_after_days = int(app.config[constants.KEY_CONFIG_WORKER_PRUNE_AFTER_DAYS])
    next_prune_time = datetime_now()

    log("Entering main loop.", LogLevel.INFOLOW)
    while True:
        log("Starting work.")

        with app.app_context():
            ds = get_download_set()

            if ds:
                repo.reset_items_in_progress(ds.id)
                di = repo.get_oldest_queued_download_item(ds.id)

                if di is None:
                    log(
                        f"No items for download set '{ds.id}' left in queue.",
                        LogLevel.INFOLOW,
                    )
                    pack_up_download_items(ds)
                else:
                    do_download(
                        di,
                        args.random_fail_downloading,
                        args.random_fail_finalizing,
                    )

            if not ds:
                if datetime_now() > next_prune_time:
                    do_prune(datetime_now() - timedelta(days=prune_after_days))
                    next_prune_time = datetime_now() + timedelta(minutes=60)
                    log(
                        f"Next prune time set to {next_prune_time}.",
                        LogLevel.INFO,
                    )

        timeout = choice(idle_wait_seconds)
        log(
            f"Sleeping for {timeout} seconds. Wake up at: {datetime_now() + timedelta(seconds=timeout)}."
        )
        sleep(timeout)
