from flask import abort, Blueprint, flash, redirect, render_template, url_for

from App.models import DownloadSet, repo

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


@downloads_blueprint.get('/<id>/view_items')
def view_items(id):
    abort(501)

class DownloadSetDetailsViewModel(object):
    _download_set = None
    _count_download_items = 0
    id = None

    def __init__(self, download_set: DownloadSet, count_download_items: int):
        self._download_set = download_set
        self._count_download_items = count_download_items

        self.id = download_set.id

    def get_properties_for_display(self):
        return [
            ('Items', self._count_download_items)
        ] + self._download_set.get_properties_for_display()