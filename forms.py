from flask_wtf import Form
from wtforms import StringField, IntegerField, RadioField, PasswordField,BooleanField, SelectField

from wtforms.fields import DateTimeField, DateField, EmailField

from wtforms.validators import DataRequired, NumberRange, Email, EqualTo, Length

class LoginForm(Form):
    email = EmailField('Enter Email', validators=[DataRequired(), Email()])
    password = PasswordField('Enter Password', validators=[DataRequired(), Length(min=4,message='Must be at least 4 characters')])

class Register(Form):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired(), Email()])
    company = StringField('Company', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match'), Length(min=4,message='Must be at least 4 characters')])
    password2 = PasswordField('conform password', validators=[DataRequired(), Length(min=4,message='Must be at least 4 characters')])
