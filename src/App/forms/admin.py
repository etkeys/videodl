from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, EmailField, SubmitField
from wtforms.validators import DataRequired


class AddEditUserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    is_admin = BooleanField("Is Admin", default=False)

    submit = SubmitField("Submit")

    for_edit = False

    def __init__(self, for_edit=False, *args, **kwargs):
        super(AddEditUserForm, self).__init__(*args, **kwargs)
        self.for_edit = for_edit
