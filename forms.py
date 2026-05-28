from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, TextAreaField, FloatField, DateField,
    SelectField, PasswordField, SubmitField
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class PropertyForm(FlaskForm):
    name = StringField('Property Name', validators=[DataRequired(), Length(max=200)])
    address = TextAreaField('Address', validators=[DataRequired()])
    property_type = SelectField('Property Type', choices=[
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('studio', 'Studio'),
        ('commercial', 'Commercial'),
        ('land', 'Land'),
        ('other', 'Other')
    ])
    status = SelectField('Status', choices=[
        ('vacant', 'Vacant'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance')
    ])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save')


class ContractForm(FlaskForm):
    tenant_name = StringField('Tenant Name', validators=[DataRequired(), Length(max=200)])
    tenant_phone = StringField('Phone Number', validators=[Optional(), Length(max=50)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    rent_amount = FloatField('Monthly Rent ($)', validators=[DataRequired(), NumberRange(min=0)])
    deposit = FloatField('Deposit ($)', validators=[Optional(), NumberRange(min=0)])
    contract_file = FileField('Contract File (PDF or Image)', validators=[
        Optional(),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'], 'PDF or images only')
    ])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add Contract')


class PhotoForm(FlaskForm):
    photo_type = SelectField('Photo Type', choices=[
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('facade', 'Facade'),
        ('other', 'Other')
    ])
    photo_file = FileField('Photo', validators=[
        DataRequired(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'], 'Images only')
    ])
    description = StringField('Description', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Upload')
