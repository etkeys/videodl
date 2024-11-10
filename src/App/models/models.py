import enum
from functools import total_ordering

from flask_login import UserMixin
from sqlalchemy import Boolean, Integer, String, TIMESTAMP
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.types import Enum as SqlEnum

from App import db, utils


@total_ordering
class LogLevel(enum.Enum):
    DEBUG = 1
    INFOLOW = 2
    INFO = 3
    WARNING = 4
    ERROR = 5

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        raise NotImplementedError

    def __str__(self):
        return self.name

    @staticmethod
    def get_label(level):
        if level == LogLevel.DEBUG:
            return "[DBG]"
        if level in [LogLevel.INFO, LogLevel.INFOLOW]:
            return "[INF]"
        if level == LogLevel.WARNING:
            return "[WRN]"
        if level == LogLevel.ERROR:
            return "[ERR]"
        raise IndexError(f"Value for level not acceptable: {level}.")


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
    PACKING_FAILED = 4

    def __str__(self):
        if self == DownloadSetStatus.PACKING_FAILED:
            return "PACKING FAILED"
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = mapped_column(String(36), primary_key=True, default=utils.new_id)
    auth_id = mapped_column(
        String(36), unique=True, nullable=False, default=utils.new_id
    )
    email = mapped_column(String(255), unique=True, nullable=False)
    name = mapped_column(String(255), unique=True, nullable=False)
    pw_hash = mapped_column(String(60), nullable=False)
    is_admin = mapped_column(Boolean(), nullable=False, default=False)

    downloads = relationship("DownloadSet", back_populates="user")

    def __repr__(self):
        return f"('{self.name}', '{self.email}')"

    def get_id(self):
        return self.auth_id


class DownloadSet(db.Model):
    __tablename__ = "download_sets"
    id = mapped_column(String(36), primary_key=True, default=utils.new_id)
    user_id = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status = mapped_column(
        SqlEnum(DownloadSetStatus), nullable=False, default=DownloadSetStatus.TODO
    )
    created_datetime = mapped_column(
        TIMESTAMP(), nullable=False, default=utils.datetime_now
    )
    queued_datetime = mapped_column(TIMESTAMP())
    completed_datetime = mapped_column(TIMESTAMP())
    archive_path = mapped_column(String(255))

    items = relationship("DownloadItem", back_populates="download_set")
    user = relationship("User", back_populates="downloads")

    def belongs_to_user(self, user_id):
        return self.user_id == user_id

    def get_properties_for_display(self, include_admin_props: bool | None = False):
        ret = [
            ("Status", self.status),
            ("Created", utils.maybe_datetime_to_display_string(self.created_datetime)),
            ("Queued", utils.maybe_datetime_to_display_string(self.queued_datetime)),
            (
                "Completed",
                utils.maybe_datetime_to_display_string(self.completed_datetime),
            ),
        ]
        if include_admin_props:
            ret += [
                ("Id", self.id),
                ("Archive", "" if self.archive_path is None else self.archive_path),
            ]
        return ret

    def is_completed(self):
        return self.status == DownloadSetStatus.COMPLETED

    def is_packing_failed(self):
        return self.status == DownloadSetStatus.PACKING_FAILED

    def is_processing(self):
        return self.status == DownloadSetStatus.PROCESSING

    def is_queued(self):
        return self.status == DownloadSetStatus.QUEUED

    def is_terminated(self):
        return self.is_completed() or self.is_packing_failed()

    def is_todo(self):
        return self.status == DownloadSetStatus.TODO


class DownloadItem(db.Model):
    __tablename__ = "download_items"
    id = mapped_column(String(36), primary_key=True, default=utils.new_id)
    status = mapped_column(
        SqlEnum(DownloadItemStatus), nullable=False, default=DownloadItemStatus.TODO
    )
    artist = mapped_column(String(50))
    title = mapped_column(String(100), nullable=False)
    audio_only = mapped_column(Boolean(), nullable=False, default=False)
    url = mapped_column(String(255), nullable=False)
    file_name = mapped_column(String(255), nullable=False)
    added_datetime = mapped_column(
        TIMESTAMP(), nullable=False, default=utils.datetime_now
    )
    download_set_id = mapped_column(
        String(36), ForeignKey("download_sets.id"), nullable=False
    )
    copied_from_id = mapped_column(String(36), ForeignKey("download_items.id"))

    copied_from = relationship("DownloadItem", back_populates="copied_to")
    copied_to = relationship(
        "DownloadItem", back_populates="copied_from", remote_side=[id]
    )
    download_set = relationship("DownloadSet", back_populates="items")

    def __repr__(self):
        return f"DownloadItem('{self.id}', '{self.url}', '{self.artist}', '{self.title}', audio_only={self.audio_only})"

    def belongs_to_set(self, download_set_id):
        return self.download_set_id == download_set_id

    def get_properties_for_display(self, include_admin_props: bool | None = False):
        ret = [
            ("Author/Artist", "" if self.artist is None else self.artist),
            ("Title", self.title),
            ("Audio Only", "Yes" if self.audio_only else "No"),
            ("URL", self.url),
            ("Status", self.status),
        ]
        if include_admin_props:
            ret += [
                ("Id", self.id),
                (
                    "Copied From",
                    "" if self.copied_from_id is None else self.copied_from_id,
                ),
            ]
        return ret

    def is_copied_from(self, other_id):
        return self.copied_from_id == other_id

    def is_failed(self):
        return self.status == DownloadItemStatus.FAILED

    def is_queued(self):
        return self.status == DownloadItemStatus.QUEUED

    def is_terminated(self):
        return (
            self.status == DownloadItemStatus.COMPLETED
            or self.status == DownloadItemStatus.FAILED
        )

    def is_todo(self):
        return self.status == DownloadItemStatus.TODO


class WorkerMessage(db.Model):
    __tablename__ = "worker_messages"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    recorded_datetime = mapped_column(
        TIMESTAMP(), nullable=False, unique=True, default=utils.datetime_now
    )
    level = mapped_column(SqlEnum(LogLevel), nullable=False)
    message = mapped_column(String, nullable=False)
