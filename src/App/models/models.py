from datetime import datetime, timezone
import enum
import uuid

from flask_login import UserMixin

from App import utils

class User(UserMixin):
    id = None
    email = None
    name = None
    access_token = None
    is_admin = None

    def __init__(self, email, name, access_token, is_admin = False, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.email = email
        self.name = name
        self.access_token = access_token
        self.is_admin = is_admin

    def __repr__(self):
        return f"('{self.name}', '{self.email}')"

class DownloadItem(object):
    id = None
    status = None
    title = None
    audio_only = None
    url = None
    added_datetime = None
    download_set_id = None
    copied_from_id = None

    def __init__(self, download_set_id, url, **kwargs):
        if download_set_id is None or not is_valid_uuid(download_set_id):
            raise ValueError(f"Value for argument download_set_id is not a valid uuid: {download_set_id}.")
        if url is None:
            raise ValueError(f"Value for argument url cannot be None.")

        self.download_set_id = download_set_id
        self.url = url

        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.status = kwargs.get('status', DownloadItemStatus.TODO)
        self.title = kwargs.get('title', self.id)
        self.audio_only = kwargs.get('audio_only', False)
        self.added_datetime = kwargs.get('added_datetime', datetime.now(timezone.utc))
        self.copied_from_id = kwargs.get('copied_from_id', None)

    def __repr__(self):
        return f"DownloadItem('{self.id}', '{self.url}', '{self.title}', audio_only={self.audio_only})"

    def get_properties_for_display(self):
        return [
            ('Title', self.title),
            ('Audio Only', 'Yes' if self.audio_only else 'No'),
            ('URL', self.url),
            ('Status', self.status)
        ]

    def is_failed(self):
        return self.status == DownloadItemStatus.FAILED

    def is_todo(self):
        return self.status == DownloadItemStatus.TODO

class DownloadSet(object):
    id = None
    status = None
    created_datetime = None
    queued_datetime = None
    completed_datetime = None

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.status = kwargs.get('status', DownloadSetStatus.TODO)
        self.created_datetime = kwargs.get('created_datetime', datetime.now(timezone.utc))
        self.queued_datetime = kwargs.get('queued_datetime', None)
        self.completed_datetime = kwargs.get('completed_datetime', None)

    def get_properties_for_display(self):
        return [
            ('Status', str(self.status)),
            ('Created', utils.maybe_datetime_to_display_string(self.created_datetime)),
            ('Queued', utils.maybe_datetime_to_display_string(self.queued_datetime)),
            ('Completed', utils.maybe_datetime_to_display_string(self.completed_datetime))
        ]

    def is_completed(self):
        return self.status == DownloadSetStatus.COMPLETED

    def is_todo(self):
        return self.status == DownloadSetStatus.TODO

class DownloadItemStatus(enum.Enum):
    TODO = 0
    QUEUED = 1
    DOWNLOADING = 2
    FINALIZING = 3
    COMPLETED = 4
    FAILED = 5

    def __str__(self):
        return self.name

class DownloadSetStatus(enum.Enum):
    TODO = 0
    QUEUED = 1
    PROCESSING = 2
    COMPLETED = 3

    def __str__(self):
        return self.name


# Taken from stackoverflow (by Martin Thoma)
# https://stackoverflow.com/a/33245493
def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test