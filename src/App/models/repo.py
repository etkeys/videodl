
from .models import *

import uuid
from datetime import datetime, timezone, timedelta
_init_datetime = datetime.now(timezone.utc)
download_sets = [
        DownloadSet(
            id=str(uuid.uuid4()),
            status=DownloadSetStatus.COMPLETED,
            created_datetime=_init_datetime - timedelta(days=3),
            queued_datetime=_init_datetime - timedelta(days=2, hours=23),
            completed_datetime=_init_datetime - timedelta(days=2, hours=21),
        ),
        DownloadSet(
            id=str(uuid.uuid4()),
            status=DownloadSetStatus.PROCESSING,
            created_datetime=_init_datetime - timedelta(days=2),
            queued_datetime=_init_datetime - timedelta(days=1, hours=16)
        ),
        DownloadSet()
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

    def add_todo_download_item(self, item: DownloadItem):
        if not item.is_todo():
            raise ValueError('Can only add new item if it is in "TODO" status.')
        ds = next((i for i in download_sets if i.id == item.download_set_id), None)
        if ds is None:
            raise ValueError(f"DownloadSet (ID: {item.download_set_id}) does not exist.")
        if not ds.is_todo():
            raise ValueError(f'Cannot add item to DownloadSet not in "TODO" status.')
        if next((i for i in download_items if i.id == item.id), None) != None:
            raise ValueError(f'Item already exists')

        download_items.append(item)

    def copy_download_item_to_todo(self, item: DownloadItem):
        if next((i for i in self.get_todo_download_items() if i.copied_from_id == item.id), None):
            return

        new_item = DownloadItem(
            download_set_id=repo.get_todo_download_set().id,
            url=item.url,
            title=item.title,
            audio_only=item.audio_only,
            copied_from_id=item.id
        )
        download_items.append(new_item)

    def count_items_in_download_set(self, download_set_id):
        return len(self.get_download_items(download_set_id))

    def delete_todo_download_items(self):
        items = self.get_todo_download_items()
        for item in items:
            self.delete_todo_download_item_by_id(item.id)

    def delete_todo_download_item_by_id(self, id):
        idx = next((i for i,x in enumerate(download_items) if x.id == id), None)
        if idx is not None:
            del download_items[idx]

    def get_download_set_by_id(self, id):
        return next((i for i in download_sets if i.id == id), None)

    def get_download_sets(self):
        return [i for i in download_sets]

    def get_download_items(self, download_set_id, where = None):
        result = [i for i in download_items if i.download_set_id == download_set_id]
        if not where is None:
            result = filter(where, result)
        return list(result)

    def get_download_items_failed(self, download_set_id):
        return [i for i in download_items if i.download_set_id == download_set_id and
                                                i.is_failed()]

    def get_download_item_by_id(self, item_id):
        return next((i for i in download_items if i.id == item_id), None)

    def get_todo_download_set(self):
        result = next((ds for ds in download_sets if ds.status == DownloadSetStatus.TODO), None)
        if result is None:
            download_sets.append(DownloadSet())
            result = download_sets[-1]
        return result

    def get_todo_download_items(self):
        ds_id = self.get_todo_download_set().id
        return [i for i in download_items if i.download_set_id == ds_id]

    def get_todo_download_item_by_id(self, id):
        return next((i for i in download_items if i.id == id and i.status == DownloadItemStatus.TODO), None)

    def is_item_copied_to_todo(self, item: DownloadItem):
        return True if next((i for i in download_items if i.copied_from_id == item.id), None) else False

    def submit_todo_items(self):
        ds = self.get_todo_download_set()
        ds.status = DownloadSetStatus.QUEUED
        for item in self.get_todo_download_items():
            item.status = DownloadItemStatus.QUEUED

repo = Repository()

