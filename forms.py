from flask_wtf import Form, FlaskForm
from wtforms import StringField, IntegerField, RadioField, PasswordField,BooleanField, SelectField,TextAreaField

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

class SendCertificates(FlaskForm):
    sender = EmailField('sender', validators=[ DataRequired(),Email()])
    recipient = EmailField('Recipient', validators=[DataRequired(), Email()])
    po_number = StringField('PO number', validators=[DataRequired()])
    batch_number = StringField('Batch Number')
    part_number = StringField('Part Number')
    assembly_number = StringField('Assembly Number')
    manufacturing_country = StringField('Manufacturing Country')
    reach_compliant = BooleanField('Reach Compliant?')
    hazardous = BooleanField('Hazardous?')
    material_expiry_date = StringField('Material Expiry Date')
    additional_notes = TextAreaField('Additional Notes')

