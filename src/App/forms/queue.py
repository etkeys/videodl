
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, URLField

class DeleteDownloadItemsForm(FlaskForm):
    title = StringField('Title')
    audio_only = BooleanField('Audio Only')
    url = URLField('URL')

    submit_del = SubmitField("Yes, I'm sure.", name='Submit')
    submit_can = SubmitField("No, go back.", name='Cancel')