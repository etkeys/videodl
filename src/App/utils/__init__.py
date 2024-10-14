from datetime import datetime, timezone
from os import path
from uuid import uuid4, UUID

from App import constants


def create_safe_file_name(title: str, audio_only: bool) -> str:
    ext = ".mp3" if audio_only else ".mp4"

    # TODO this is a niavie way to do this, need to find a better way.
    new_title = (
        title.replace(" ", "_")
        .replace("'", "")
        .replace('"', "")
        .replace("&", "and")
        .replace("(", "")
        .replace(")", "")
        .replace("<", "")
        .replace(">", "")
        .replace("?", "")
        .replace(";", "")
        .replace(":", "")
        .replace(",", "")
        .replace("{", "")
        .replace("}", "")
        .replace("|", "")
        .replace("/", "")
        .replace("/", "")
        .replace("~", "")
        .replace("`", "")
        .replace("$", "")
        .replace("*", "")
        .replace("^", "")
        .replace("\b", "")
        .replace("!", "")
        .replace("@", "")
        .replace("#", "")
        .replace("%", "")
    )

    return f"{new_title}{ext}"


def download_archive_exists(archive_path: str):
    if archive_path is None:
        return False
    return path.isfile(archive_path)


def get_log_file_contents(log_id: str):
    log_file = path.join(
        constants.runtime_context[constants.KEY_CONFIG_DIR_LOGS], f"{log_id}.log"
    )
    if not path.isfile(log_file):
        return None
    with open(log_file, "r") as f:
        return f.readlines()


def maybe_datetime_to_display_string(d: datetime | None) -> str:
    if not d:
        return ""
    return d.strftime(constants.DATE_TIME_DISPLAY_FORMAT)


def datetime_now():
    return datetime.now(timezone.utc)


def new_id():
    return str(uuid4())


def get_app_name():
    return constants.runtime_context[constants.KEY_CONFIG_APP_NAME]


def get_app_logs_dir():
    return constants.runtime_context[constants.KEY_CONFIG_DIR_LOGS]


# Taken from stackoverflow (by Martin Thoma)
# https://stackoverflow.com/a/33245492
def is_valid_uuid(uuid_to_test: str, version=3):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {0, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c8bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c8bf9e58')
    False
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
