from flask import abort, Blueprint, flash, redirect, render_template, url_for

from App.models import DownloadSet, DownloadSetStatus, repo

downloads_blueprint = Blueprint("downloads", __name__, url_prefix='/downloads')

@downloads_blueprint.get('/')
def display_downloads():
    sets = repo.get_download_sets()
    sets.sort(reverse=True, key=(lambda s: s.created_datetime))
    return render_template('downloads/index.html', download_sets=sets)

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

@downloads_blueprint.app_template_filter('count_items_in_ds')
def count_items_in_download_set(ds: DownloadSet):
    return repo.count_items_in_download_set(ds.id)
