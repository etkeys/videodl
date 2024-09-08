from flask import abort, Blueprint, flash, redirect, render_template, url_for

from App.models import DownloadSet, DownloadSetStatus, repo

downloads_blueprint = Blueprint("downloads", __name__, url_prefix='/downloads')

@downloads_blueprint.get('/')
def display_downloads():
    sets = repo.get_download_sets()
    sets.sort(reverse=True, key=(lambda s: s.created_datetime))
    vms = []
    for ds in sets:
        count_items = len(repo.get_download_items(ds.id))
        vms.append(DownloadSetDetailsViewModel(ds, count_items))
    return render_template('downloads/index.html', downloads=vms)


@downloads_blueprint.get('/<id>/view')
def view_download_set(id):
    ds = repo.get_download_set_by_id(id)
    if ds is None:
        abort(404, f"Could not find download set with Id '{id}'.")
    items = repo.get_download_items(id)
    items.sort(key=(lambda i: i.added_datetime))
    return render_template('downloads/view.html', download_set=ds, download_items=items)

@downloads_blueprint.app_template_filter('is_ds_status_todo')
def is_download_set_status_todo(status: DownloadSetStatus):
    return status == DownloadSetStatus.TODO

class DownloadSetDetailsViewModel(object):
    _download_set = None
    _count_download_items = 0
    id = None
    status = None

    def __init__(self, download_set: DownloadSet, count_download_items: int):
        self._download_set = download_set
        self._count_download_items = count_download_items

        self.id = download_set.id
        self.status = download_set.status

    def get_properties_for_display(self):
        return [
            ('Items', self._count_download_items)
        ] + self._download_set.get_properties_for_display()