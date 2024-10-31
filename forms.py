from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError, DataRequired, EqualTo
from models import User

class RegisterForm(FlaskForm):
    """User registration form."""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class UserUpdateForm(FlaskForm):
    """User update form."""
    username = StringField("Username", validators=[InputRequired()])
    #password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])


class PlaylistForm(FlaskForm):
    """Form for adding a video to a playlist."""
    name = StringField("Playlist Name", validators=[InputRequired()])


class RequestResetForm(FlaskForm):
    """Form for requesting a password reset."""
    email = StringField("Email", validators=[InputRequired()])
    submit = SubmitField("Request Password Reset")
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email. You must register first.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class DeleteForm(FlaskForm):
    """Delete form -- this form is intentionally blank."""