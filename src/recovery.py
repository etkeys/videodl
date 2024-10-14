# This script will provide an access token to the "recovery" special user.
# This users is an admin and can reset accounts in the event of loss o
# access tokens.

from App import create_app
from App.models.repo import repo
from App.utils.Authentication import create_new_credentials


if __name__ == "__main__":
    app = create_app()

    new_auth_id, new_pw_hash, new_access_token = create_new_credentials()

    try:
        with app.app_context():
            user_id = repo.get_user_by_name("recovery").id
            repo.update_user(user_id, auth_id=new_auth_id, pw_hash=new_pw_hash)
        print(f"Recovery access token = '{new_access_token}'")
    except Exception as ex:
        print(f"Unable to reset recovery account. {ex}")
