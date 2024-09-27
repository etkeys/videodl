from sqlalchemy.orm import aliased, joinedload

from .models import *

from App import db, login_manager
from App.utils.Exceptions import NotFoundError


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
    def get_oldest_queued_download_item(self, download_set_id):
        queued_items = sorted(
            [
                i
                for i in download_items
                if i.belongs_to_set(download_set_id) and i.is_queued()
            ],
            key=(lambda x: x.added_datetime),
        )
        return next((i for i in queued_items), None)

    def get_oldest_queued_download_set(self) -> DownloadSet | None:
        queued_sets = sorted(
            [i for i in download_sets if i.is_queued()],
            key=(lambda x: x.queued_datetime),
        )
        return next((i for i in queued_sets), None)

    def get_processing_download_set(self):
        return next((i for i in download_sets if i.is_processing()), None)

    def update_download_item_status(
        self, di: DownloadItem, new_status: DownloadItemStatus
    ):
        di.status = new_status

    def update_download_set_status(
        self, ds: DownloadSet, new_status: DownloadSetStatus, **kwargs
    ):
        ds.status = new_status
        if ds.is_completed():
            ds.completed_datetime = datetime.now(timezone.utc)
            ds.archive_path = kwargs["archive_path"]


repo = Repository()

worker_repo = WorkerRepository()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))
