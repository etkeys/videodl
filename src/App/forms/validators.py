from wtforms import ValidationError

class UrlExists(object):
    def __init__(self, message=None):
        if not message:
            message = f"URL does not exist."
        self.message = message

    def __call__(self, form, field):
        import requests
        url = field.data
        req = requests.get(url)
        if req.status_code != 200:
            raise ValidationError(self.message)

