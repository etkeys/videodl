from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField
from wtforms.validators import DataRequired


class AuthenticateForm(FlaskForm):
    access_token = PasswordField("Access Token", validators=[DataRequired()])
    submit = SubmitField("Authenticate")
