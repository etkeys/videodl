from base64 import b64decode, b64encode

from App import bcrypt
from App.utils import new_id


def check_password(expected: str, to_check: str):
    return bcrypt.check_password_hash(expected, to_check)


def create_new_credentials():
    new_auth_id = new_id()
    new_pw = new_id()
    new_pw_hash = bcrypt.generate_password_hash(new_pw).decode("utf-8")
    new_token = b64encode(f"{new_auth_id}_{new_pw}".encode("utf-8")).decode("utf-8")

    return (new_auth_id, new_pw_hash, new_token)


def decode_token(token: str):
    decoded = b64decode(token.strip()).decode("utf-8").split("_")
    if len(decoded) != 2:
        raise ValueError("Provided token is corrupted.")
    return (decoded[0], decoded[1])
