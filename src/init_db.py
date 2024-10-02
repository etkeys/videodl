from argparse import ArgumentParser
from datetime import timedelta
from os import path

from App import bcrypt, db, constants, create_app
from App.models import *
from App.utils import datetime_now


parser = ArgumentParser(
    prog="Video DL (init db)",
    description="Script to initialize a database",
    add_help=True,
)

parser.add_argument(
    "-c",
    "--config",
    action="store",
    default=constants.DEFAULT_CONFIG_FILE,
    help=f"Path to the config file to load. Paths are relative to run.py. (default: {constants.DEFAULT_CONFIG_FILE})",
)

if __name__ == "__main__":
    args = parser.parse_args()

    script_dir = path.dirname(path.abspath(__file__))

    app = create_app(args.config, "app_config", script_dir)

    now_time = datetime_now()
    with app.app_context():
        db.create_all()

        users = [
            User(
                id="d6c8cbb6-9ab6-4f36-b933-9b6ee8a471b8",
                email="alice@example.com",
                name="Alice",
                pw_hash=bcrypt.generate_password_hash(
                    "7a3d99b983ca418b85a69c7c56778cd5"
                ).decode("utf-8"),
                is_admin=True,
            ),
            User(
                email="bob@example.com",
                name="Bob",
                pw_hash=bcrypt.generate_password_hash(
                    "7b330012fd834268945a90717e7a06d0"
                ).decode("utf-8"),
                id="6fb66c6b-9592-48da-affa-6fa887f241a6",
            ),
        ]

        download_sets = [
            DownloadSet(
                id="ad886992-6caa-4937-ae44-5d58ed7d575b",
                user_id="d6c8cbb6-9ab6-4f36-b933-9b6ee8a471b8",
                status=DownloadSetStatus.COMPLETED,
                created_datetime=now_time - timedelta(days=3),
                queued_datetime=now_time - timedelta(days=2, hours=23),
                completed_datetime=now_time - timedelta(days=2, hours=21),
            ),
            DownloadSet(
                id="ecfab23e-5658-43f4-96a4-edb3f644041d",
                user_id="6fb66c6b-9592-48da-affa-6fa887f241a6",
                status=DownloadSetStatus.QUEUED,
                created_datetime=now_time - timedelta(days=2),
                queued_datetime=now_time - timedelta(days=1, hours=16),
            ),
            DownloadSet(
                id="c0284624-df1c-495b-b41d-3ca52f5af4e0",
                user_id="d6c8cbb6-9ab6-4f36-b933-9b6ee8a471b8",
            ),
        ]

        download_items = [
            DownloadItem(
                download_set_id="ad886992-6caa-4937-ae44-5d58ed7d575b",
                url="https://foo.com/1",
                title="Download set 1 #1",
                added_datetime=now_time - timedelta(days=2, hours=23, minutes=30),
                status=DownloadItemStatus.FAILED,
            ),
            DownloadItem(
                download_set_id="ad886992-6caa-4937-ae44-5d58ed7d575b",
                url="https://foo.com/2",
                title="Download set 1 #2",
                added_datetime=now_time - timedelta(days=2, hours=23, minutes=23),
                status=DownloadItemStatus.FAILED,
            ),
            DownloadItem(
                download_set_id="ecfab23e-5658-43f4-96a4-edb3f644041d",
                url="https://bar.com/1",
                title="Download set 2 #1",
                added_datetime=now_time - timedelta(days=1, hours=23, minutes=30),
                status=DownloadItemStatus.QUEUED,
            ),
            DownloadItem(
                download_set_id="ecfab23e-5658-43f4-96a4-edb3f644041d",
                url="https://bar.com/2",
                title="Download set 2 #2",
                added_datetime=now_time - timedelta(days=1, hours=20, minutes=43),
                status=DownloadItemStatus.QUEUED,
            ),
            DownloadItem(
                download_set_id="ecfab23e-5658-43f4-96a4-edb3f644041d",
                url="https://bar.com/3",
                title="Download set 2 #3",
                added_datetime=now_time - timedelta(days=1, hours=20, minutes=16),
                status=DownloadItemStatus.QUEUED,
            ),
            DownloadItem(
                download_set_id="ecfab23e-5658-43f4-96a4-edb3f644041d",
                url="https://bar.com/4",
                title="Download set 2 #4",
                added_datetime=now_time - timedelta(days=1, hours=19, minutes=57),
                status=DownloadItemStatus.QUEUED,
            ),
            DownloadItem(
                download_set_id="c0284624-df1c-495b-b41d-3ca52f5af4e0",
                url="https://example.com/1",
                title="Video #1",
                audio_only=True,
            ),
            DownloadItem(
                download_set_id="c0284624-df1c-495b-b41d-3ca52f5af4e0",
                url="https://example.com/2",
                title="Video #2",
            ),
            DownloadItem(
                download_set_id="c0284624-df1c-495b-b41d-3ca52f5af4e0",
                url="https://example.com/3",
                title="Video #3",
            ),
        ]

        db.session.add_all(users)
        db.session.add_all(download_sets)
        db.session.add_all(download_items)
        db.session.commit()
