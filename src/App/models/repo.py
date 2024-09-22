
from .models import *

from App import bcrypt, login_manager
from App.utils.Exceptions import UnauthorizedError


import uuid
from datetime import datetime, timezone, timedelta
_init_datetime = datetime.now(timezone.utc)
users = [
    User(
        email="alice@example.com",
        name="Alice",
        access_token=bcrypt.generate_password_hash('7a3d99b983ca418b85a69c7c56778cd5').decode('utf-8'),
        is_admin=True,
        id='d6c8cbb6-9ab6-4f36-b933-9b6ee8a471b8'
    ),
    User(
        email="bob@example.com",
        name="Bob",
        access_token=bcrypt.generate_password_hash('7b330012fd834268945a90717e7a06d0').decode('utf-8'),
        id='6fb66c6b-9592-48da-affa-6fa887f241a6'
    ),
]
download_sets = [
        DownloadSet(
            user_id='d6c8cbb6-9ab6-4f36-b933-9b6ee8a471b8',
            id=str(uuid.uuid4()),
            status=DownloadSetStatus.COMPLETED,
            created_datetime=_init_datetime - timedelta(days=3),
            queued_datetime=_init_datetime - timedelta(days=2, hours=23),
            completed_datetime=_init_datetime - timedelta(days=2, hours=21),
        ),
        DownloadSet(
            user_id='6fb66c6b-9592-48da-affa-6fa887f241a6',
            id=str(uuid.uuid4()),
            status=DownloadSetStatus.QUEUED,
            created_datetime=_init_datetime - timedelta(days=2),
            queued_datetime=_init_datetime - timedelta(days=1, hours=16)
        ),
        DownloadSet(user_id='d6c8cbb6-9ab6-4f36-b933-9b6ee8a471b8')
    ]
download_items = [
    DownloadItem(
        download_set_id=download_sets[0].id,
        url='https://foo.com/1',
        title='Download set 1 #1',
        added_datetime=_init_datetime - timedelta(days=2, hours=23, minutes=30),
        status=DownloadItemStatus.FAILED
    ),
    DownloadItem(
        download_set_id=download_sets[0].id,
        url='https://foo.com/2',
        title='Download set 1 #2',
        added_datetime=_init_datetime - timedelta(days=2, hours=23, minutes=23),
        status=DownloadItemStatus.FAILED
    ),
    DownloadItem(
        download_set_id=download_sets[1].id,
        url='https://bar.com/1',
        title='Download set 2 #1',
        added_datetime=_init_datetime - timedelta(days=1, hours=23, minutes=30),
        status=DownloadItemStatus.COMPLETED
    ),
    DownloadItem(
        download_set_id=download_sets[1].id,
        url='https://bar.com/2',
        title='Download set 2 #2',
        added_datetime=_init_datetime - timedelta(days=1, hours=20, minutes=43),
        status=DownloadItemStatus.FAILED
    ),
    DownloadItem(
        download_set_id=download_sets[1].id,
        url='https://bar.com/3',
        title='Download set 2 #3',
        added_datetime=_init_datetime - timedelta(days=1, hours=20, minutes=16),
        status=DownloadItemStatus.DOWNLOADING
    ),
    DownloadItem(
        download_set_id=download_sets[1].id,
        url='https://bar.com/4',
        title='Download set 2 #4',
        added_datetime=_init_datetime - timedelta(days=1, hours=19, minutes=57),
        status=DownloadItemStatus.QUEUED
    ),
    DownloadItem(
        download_set_id=download_sets[2].id,
        url='https://example.com/1',
        title='Video #1',
        audio_only=True),
    DownloadItem(
        download_set_id=download_sets[2].id,
        url='https://example.com/2',
        title='Video #2'),
    DownloadItem(
        download_set_id=download_sets[2].id,
        url='https://example.com/3',
        title='Video #3')
]

class Repository(object):

    def add_todo_download_item(self, user_id, item: DownloadItem):
        if not item.is_todo():
            raise ValueError('Can only add new item if it is in "TODO" status.')
        ds = self.get_todo_download_set(user_id)
        if not item.belongs_to_set(ds.id):
            raise ValueError("Cannot add item because it does not belong to a Download Set that is in TODO.")
        if any(i.id == item.id for i in download_items):
            raise ValueError(f'Item already exists')

        download_items.append(item)

    def copy_download_item_to_todo(self, user_id, item: DownloadItem):
        if self.get_download_set_by_id(user_id, item.download_set_id) is None:
            raise UnauthorizedError('Could not find originating Download Set for user.')
        
        if any(i.is_copied_from(item.id) for i in self.get_todo_download_items(user_id)):
            return

        new_item = DownloadItem(
            download_set_id=repo.get_todo_download_set(user_id).id,
            url=item.url,
            title=item.title,
            audio_only=item.audio_only,
            copied_from_id=item.id
        )
        download_items.append(new_item)

    def count_items_in_download_set(self, user_id, download_set_id):
        return len(self.get_download_items(user_id, download_set_id))

    def delete_todo_download_items(self, user_id):
        items = self.get_todo_download_items(user_id)
        for item in items:
            self.delete_todo_download_item_by_id(user_id, item.id)

    def delete_todo_download_item_by_id(self, user_id, id):
        ix = next(((i, x) for i,x in enumerate(download_items) if x.id == id), None)
        if ix is not None:
            if any(ix[1].belongs_to_set(ds.id) and ds.belongs_to_user(user_id) for ds in download_sets):
                del download_items[ix[0]]

    def get_download_set_by_id(self, user_id, id):
        return next((i for i in download_sets if i.id == id
                                                and i.belongs_to_user(user_id)), None)

    def get_download_sets(self, user_id):
        return [i for i in download_sets if i.belongs_to_user(user_id)]

    def get_download_items(self, user_id, download_set_id):
        ds = self.get_download_set_by_id(user_id, download_set_id)
        if not ds is None:
            return [i for i in download_items if i.belongs_to_set(ds.id)]
        else:
            return []

    def get_download_items_failed(self, user_id, download_set_id):
        ds = self.get_download_set_by_id(user_id, download_set_id)
        if not ds is None:
            return [i for i in download_items if i.belongs_to_set(ds.id)
                                                and i.is_failed()]
        else:
            return []

    def get_download_item_by_id(self, user_id, item_id):
        item = next((i for i in download_items if i.id == item_id), None)
        if item is None:
            return None
        if any(item.belongs_to_set(ds.id)
               and ds.belongs_to_user(user_id)
               for ds in download_sets):
            return item
        else:
            return None

    def get_todo_download_set(self, user_id):
        result = next((ds for ds in download_sets if ds.belongs_to_user(user_id)
                                                    and ds.is_todo()), None)
        if result is None:
            download_sets.append(DownloadSet(user_id=user_id))
            result = download_sets[-1]
        return result

    def get_todo_download_items(self, user_id):
        ds = self.get_todo_download_set(user_id)
        return [i for i in download_items if i.belongs_to_set(ds.id)]

    def get_todo_download_item_by_id(self, user_id, id):
        ds = self.get_todo_download_set(user_id)
        item = next((i for i in download_items if i.belongs_to_set(ds.id)
                                                and i.is_todo()
                                                and i.id == id), None)
        return item

    def get_user_by_id(self, id):
        return next((i for i in users if i.id == id), None)

    def get_user_by_name(self, name):
        name = name.casefold()
        return next((i for i in users if i.name.casefold() == name), None)

    def is_item_copied_to_todo(self, user_id, item: DownloadItem):
        return any(i.is_copied_from(item.id) for i in self.get_todo_download_items(user_id))

    def submit_todo_items(self, user_id):
        ds = self.get_todo_download_set(user_id)
        ds.status = DownloadSetStatus.QUEUED
        for item in self.get_todo_download_items(user_id):
            item.status = DownloadItemStatus.QUEUED

class WorkerRepository():
    def get_oldest_queued_download_set(self) -> DownloadSet | None:
        queued_sets = sorted([i for i in download_sets if i.is_queued()], key=(lambda x: x.queued_datetime))
        return next((i for i in queued_sets), None)

    def get_processing_download_set(self):
        return next((i for i in download_sets if i.is_processing()), None)

    def update_download_set_status(self, ds: DownloadSet, status: DownloadSetStatus):
        ds.status = status



repo = Repository()

worker_repo = WorkerRepository()


@login_manager.user_loader
def load_user(user_id):
    return repo.get_user_by_id(user_id)