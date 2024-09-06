
from .models import *

download_sets = [DownloadSet()]
download_items = [
    DownloadItem(
        download_set_id=download_sets[0].id,
        url='https://example.com/1',
        title='Video #1',
        audio_only=True),
    DownloadItem(
        download_set_id=download_sets[0].id,
        url='https://example.com/2',
        title='Video #2'),
    DownloadItem(
        download_set_id=download_sets[0].id,
        url='https://example.com/3',
        title='Video #3')
]

class Repository(object):

    def add_todo_download_item(self, item: DownloadItem):
        if item.status != DownloadItemStatus.TODO:
            raise ValueError('Can only add new item if it is in "TODO" status.')
        ds = next((i for i in download_sets if i.id == item.download_set_id), None)
        if ds is None:
            raise ValueError(f"DownloadSet (ID: {item.download_set_id}) does not exist.")
        if ds.status != DownloadSetStatus.TODO:
            raise ValueError(f'Cannot add item to DownloadSet not in "TODO" status.')
        if next((i for i in download_items if i.id == item.id), None) != None:
            raise ValueError(f'Item already exists')

        download_items.append(item)

    def delete_todo_download_items(self):
        items = self.get_todo_download_items()
        for item in items:
            self.delete_todo_download_item_by_id(item.id)

    def delete_todo_download_item_by_id(self, id):
        idx = next((i for i,x in enumerate(download_items) if x.id == id), None)
        if idx is not None:
            del download_items[idx]

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

    def submit_todo_items(self):
        ds = self.get_todo_download_set()
        ds.status = DownloadSetStatus.QUEUED
        for item in self.get_todo_download_items():
            item.status = DownloadItemStatus.QUEUED

repo = Repository()

# print(repo._download_sets)
# print(repo._download_items)

