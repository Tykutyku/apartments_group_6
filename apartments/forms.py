from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Please enter your name.")])
    email = StringField("Email", validators=[DataRequired(message="Please enter your email address"), Email()])
    subject = StringField("Subject", validators=[DataRequired(message="Please enter a subject.")])
    message = TextAreaField("Message", validators=[DataRequired(message="Please enter a message.")])
    submit = SubmitField("Send")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="Please enter your username.")])
    email = StringField("Email", validators=[DataRequired(message="Please enter your email."), Email(message="Invalid email address.")])
    password = PasswordField("Password", validators=[DataRequired(message="Please enter your password.")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(message="Please confirm your password."), EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(message="Please enter your email address"), Email()])
    password = PasswordField("Password", validators=[DataRequired(message="Please enter your password.")])
    submit = SubmitField("Login")
