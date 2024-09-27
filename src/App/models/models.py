import enum

from flask_login import UserMixin
from sqlalchemy import Boolean, String, TIMESTAMP
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.types import Enum as SqlEnum

from App import db, utils


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
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = "Users"
    id = mapped_column(
        String(36, collation="NOCASE"), primary_key=True, default=utils.new_id
    )
    email = mapped_column(String(255, collation="NOCASE"), unique=True, nullable=False)
    name = mapped_column(String(255, collation="NOCASE"), unique=True, nullable=False)
    access_token = mapped_column(String(60), nullable=False)
    is_admin = mapped_column(Boolean(), nullable=False, default=False)

    downloads = relationship("DownloadSet", back_populates="user")

    def __repr__(self):
        return f"('{self.name}', '{self.email}')"


class DownloadSet(db.Model):
    __tablename__ = "DownloadSets"
    id = mapped_column(
        String(36, collation="NOCASE"), primary_key=True, default=utils.new_id
    )
    user_id = mapped_column(
        String(36, collation="NOCASE"), ForeignKey("Users.id"), nullable=False
    )
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

    def get_properties_for_display(self):
        return [
            ("Status", str(self.status)),
            ("Created", utils.maybe_datetime_to_display_string(self.created_datetime)),
            ("Queued", utils.maybe_datetime_to_display_string(self.queued_datetime)),
            (
                "Completed",
                utils.maybe_datetime_to_display_string(self.completed_datetime),
            ),
        ]

    def is_completed(self):
        return self.status == DownloadSetStatus.COMPLETED

    def is_processing(self):
        return self.status == DownloadSetStatus.PROCESSING

    def is_queued(self):
        return self.status == DownloadSetStatus.QUEUED

    def is_todo(self):
        return self.status == DownloadSetStatus.TODO


class DownloadItem(db.Model):
    __tablename__ = "DownloadItems"
    id = mapped_column(
        String(36, collation="NOCASE"), primary_key=True, default=utils.new_id
    )
    status = mapped_column(
        SqlEnum(DownloadItemStatus), nullable=False, default=DownloadItemStatus.TODO
    )
    title = mapped_column(String(255, collation="NOCASE"), nullable=False)
    audio_only = mapped_column(Boolean(), nullable=False, default=False)
    url = mapped_column(String(255, collation="NOCASE"), nullable=False)
    added_datetime = mapped_column(
        TIMESTAMP(), nullable=False, default=utils.datetime_now
    )
    download_set_id = mapped_column(
        String(36, collation="NOCASE"), ForeignKey("DownloadSets.id"), nullable=False
    )
    copied_from_id = mapped_column(
        String(36, collation="NOCASE"), ForeignKey("DownloadItems.id")
    )

    copied_from = relationship("DownloadItem", back_populates="copied_to")
    copied_to = relationship(
        "DownloadItem", back_populates="copied_from", remote_side=[id]
    )
    download_set = relationship("DownloadSet", back_populates="items")

    def __repr__(self):
        return f"DownloadItem('{self.id}', '{self.url}', '{self.title}', audio_only={self.audio_only})"

    def belongs_to_set(self, download_set_id):
        return self.download_set_id == download_set_id

    def get_properties_for_display(self):
        return [
            ("Title", self.title),
            ("Audio Only", "Yes" if self.audio_only else "No"),
            ("URL", self.url),
            ("Status", self.status),
        ]

    def is_copied_from(self, other_id):
        return self.copied_from_id == other_id

    def is_failed(self):
        return self.status == DownloadItemStatus.FAILED

    def is_queued(self):
        return self.status == DownloadItemStatus.QUEUED

    def is_todo(self):
        return self.status == DownloadItemStatus.TODO
