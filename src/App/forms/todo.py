from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, URLField
from wtforms.validators import InputRequired, DataRequired
from App.forms.validators import UrlExists


class DownloadItemDetailsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    audio_only = BooleanField("Audio Only", default=True)
    url = StringField("URL", validators=[DataRequired(), UrlExists()])

    submit = SubmitField("Submit", name="Execute")

    for_delete = False

    def __init__(self, for_delete=False, *args, **kwargs):
        super(DownloadItemDetailsForm, self).__init__(*args, **kwargs)
        self.for_delete = for_delete
        if for_delete:
            self.submit.label.text = "Yes, I'm sure."
