from sqlalchemy.orm import aliased, joinedload

from .models import *

from App import db, login_manager
from App.utils import datetime_now
from App.utils.Exceptions import NotFoundError, UnauthorizedError


class Repository(object):

    def add_download_item(
        self,
        user_id: str,
        title: str,
        audio_only: bool,
        url: str,
        copy_from_id: str | None = None,
    ):
        item = (
            DownloadItem.query.join(DownloadSet)
            .where(
                DownloadSet.user_id == user_id,
                DownloadItem.url == url,
                DownloadItem.status == DownloadItemStatus.TODO,
            )
            .first()
        )

        if not item is None:
            raise ValueError(f"Item with url '{url}' already in To Do.")

        ds = self.get_todo_download_set(user_id)

        item = DownloadItem(
            title=title, audio_only=audio_only, url=url, download_set_id=ds.id
        )

        if copy_from_id is not None:
            item.copied_from_id = copy_from_id

        db.session.add(item)
        db.session.commit()

    def count_items_in_download_set(self, user_id: str, download_set_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(DownloadSet.id == download_set_id, DownloadSet.user_id == user_id)
            .count()
        )

    def delete_todo_download_items(self, user_id):
        ds = self.get_todo_download_set(user_id, load_child_items_eagerly=True)
        count = len(ds.items)
        for item in ds.items:
            db.session.delete(item)
        db.session.commit()

        return count

    def delete_todo_download_item_by_id(self, user_id: str, item_id: str):
        item = (
            DownloadItem.query.join(DownloadSet)
            .where(
                DownloadItem.id == item_id,
                DownloadItem.status == DownloadItemStatus.TODO,
                DownloadSet.user_id == user_id,
            )
            .first()
        )
        if item is not None:
            db.session.delete(item)
            db.session.commit()
            return 1
        return 0

    def count_items_in_download_set_completed(self, user_id: str, download_set_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(
                DownloadSet.user_id == user_id,
                DownloadSet.id == download_set_id,
                DownloadItem.status == DownloadItemStatus.COMPLETED,
            )
            .count()
        )

    def count_items_in_download_set_failed(self, user_id: str, download_set_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(
                DownloadSet.user_id == user_id,
                DownloadSet.id == download_set_id,
                DownloadItem.status == DownloadItemStatus.FAILED,
            )
            .count()
        )

    def get_download_set_by_id(
        self, user_id: str, download_set_id: str, load_child_items_eagerly: bool = False
    ):
        query = DownloadSet.query.filter_by(user_id=user_id, id=download_set_id)
        if load_child_items_eagerly:
            query.options(joinedload(DownloadSet.items))
        return query.first()

    def get_download_sets(self, user_id: str):
        return DownloadSet.query.filter_by(user_id=user_id).order_by(
            DownloadSet.created_datetime.desc()
        )

    def get_download_items(self, user_id: str, download_set_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(DownloadSet.id == download_set_id, DownloadSet.user_id == user_id)
            .order_by(DownloadItem.added_datetime)
            .all()
        )

    def get_download_items_failed(self, user_id: str, download_set_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(
                DownloadItem.status == DownloadItemStatus.FAILED,
                DownloadSet.id == download_set_id,
                DownloadSet.user_id == user_id,
            )
            .order_by(DownloadItem.added_datetime)
            .all()
        )

    def get_download_item_by_id(self, user_id: str, item_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(DownloadItem.id == item_id, DownloadSet.user_id == user_id)
            .first()
        )

    def get_todo_download_items(self, user_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(
                DownloadItem.status == DownloadItemStatus.TODO,
                DownloadSet.user_id == user_id,
            )
            .order_by(DownloadItem.added_datetime)
            .all()
        )

    def get_todo_download_item_by_id(self, user_id: str, item_id: str):
        return (
            DownloadItem.query.join(DownloadSet)
            .where(
                DownloadItem.id == item_id,
                DownloadItem.status == DownloadItemStatus.TODO,
                DownloadSet.user_id == user_id,
            )
            .first()
        )

    def get_todo_download_set(
        self, user_id: str, load_child_items_eagerly: bool = False
    ):
        query = DownloadSet.query.filter_by(
            user_id=user_id, status=DownloadSetStatus.TODO
        )
        if load_child_items_eagerly:
            query.options(joinedload(DownloadSet.items))
        ds = query.first()

        if ds is None:
            ds = DownloadSet(user_id=user_id)
            db.session.add(ds)
            db.session.commit()
        return ds

    def get_user_by_id(self, id: str):
        return User.query.get(id)

    def get_user_by_name(self, name: str):
        return User.query.filter_by(name=name).first()

    def get_worker_messages(self, user_id: str):
        user = self.get_user_by_id(user_id)
        if not user.is_admin:
            raise UnauthorizedError("User is not authorized for this data.")
        return WorkerMessage.query.order_by(
            WorkerMessage.recorded_datetime.desc()
        ).all()

    def is_item_copied_to_todo(self, user_id: str, item_id: str):
        downloadItem2 = aliased(DownloadItem)

        count = (
            DownloadItem.query.join(DownloadSet)
            .join(downloadItem2, DownloadItem.id == downloadItem2.copied_from_id)
            .where(
                DownloadItem.id == item_id,
                DownloadSet.user_id == user_id,
                downloadItem2.status == DownloadItemStatus.TODO,
            )
        ).count()

        return count > 0

    def submit_todo_items(self, user_id: str):
        ds = self.get_todo_download_set(user_id, load_child_items_eagerly=True)
        if len(ds.items) < 1:
            return 0

        ds.status = DownloadSetStatus.QUEUED
        for item in ds.items:
            item.status = DownloadItemStatus.QUEUED
        db.session.commit()

        return len(ds.items) + 1

    def update_item(self, user_id: str, item_id: str, **kwargs):
        item = self.get_todo_download_item_by_id(user_id, item_id)
        if item is None:
            raise NotFoundError("Could not find item in To Do status.")

        if "title" in kwargs:
            item.title = str(kwargs["title"])
        if "audio_only" in kwargs:
            item.audio_only = bool(kwargs["audio_only"])
        if "url" in kwargs:
            item.url = str(kwargs["url"])

        db.session.commit()


class WorkerRepository:
    def add_worker_message(self, level: LogLevel, message: str):
        m = WorkerMessage(level=level, message=message)
        db.session.add(m)
        db.session.commit()

    def get_oldest_queued_download_item(self, download_set_id: str):
        return (
            DownloadItem.query.filter_by(
                download_set_id=download_set_id, status=DownloadItemStatus.QUEUED
            )
            .order_by(DownloadItem.added_datetime)
            .first()
        )

    def get_oldest_queued_download_set(self):
        return (
            DownloadSet.query.filter_by(status=DownloadSetStatus.QUEUED)
            .order_by(DownloadSet.queued_datetime)
            .first()
        )

    def get_processing_download_set(self):
        return (
            DownloadSet.query.filter_by(status=DownloadSetStatus.PROCESSING)
            .order_by(DownloadSet.queued_datetime)
            .first()
        )

    def update_download_item_status(
        self, di: DownloadItem, new_status: DownloadItemStatus
    ):
        di.status = new_status
        db.session.commit()

    def update_download_set_status(
        self, ds: DownloadSet, new_status: DownloadSetStatus, archive_path: str = None
    ):
        ds.status = new_status
        if ds.is_completed():
            ds.completed_datetime = datetime_now()
            if archive_path is None:
                raise ValueError("Archive path expected, but got None.")
            ds.archive_path = archive_path

        db.session.commit()


repo = Repository()

worker_repo = WorkerRepository()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))
