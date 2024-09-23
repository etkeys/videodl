from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class AuthenticateForm(FlaskForm):
    user_name = StringField("Name", validators=[DataRequired()])
    access_token = PasswordField("Access Token", validators=[DataRequired()])
    submit = SubmitField("Authenticate")
