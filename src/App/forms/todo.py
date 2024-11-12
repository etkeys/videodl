from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, URLField
from wtforms.validators import InputRequired, DataRequired, Length
from App.forms.validators import UrlExists


class DownloadItemDetailsForm(FlaskForm):
    artist = StringField("Author/Artist", validators=[Length(max=50)])
    title = StringField("Title", validators=[DataRequired(), Length(1, 100)])
    audio_only = BooleanField("Audio Only", default=True)
    url = StringField("URL", validators=[DataRequired()])

    submit = SubmitField("Submit", name="Execute")

    for_delete = False

    def __init__(self, for_delete=False, *args, **kwargs):
        super(DownloadItemDetailsForm, self).__init__(*args, **kwargs)
        self.for_delete = for_delete
        if for_delete:
            self.submit.label.text = "Yes, I'm sure."

    def get_properties_for_display(self):
        ret = [
            ("Author/Artist", "" if self.artist is None else self.artist),
            ("Title", self.title),
            ("Audio Only", "Yes" if self.audio_only else "No"),
            ("URL", self.url),
        ]
        return ret
