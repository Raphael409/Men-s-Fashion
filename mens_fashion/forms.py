# The module is used for data submission of the web forms; registration, login, and adding products

from flask_login import current_user
from flask_wtf import FlaskForm  # used in rendering forms for web applications
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField  # importing data types of the string fields
from wtforms import (DateField, IntegerField, PasswordField, SelectField,
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import (  # validations for entry values enterded in the forms
    DataRequired, Email, EqualTo, Length, ValidationError)

from mens_fashion.models import Products, User

user = [('User'), ('Admin'),('Employee')]
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    type = SelectField('Type of user', choices=user, validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # The function ensures that there is no existing similar user name
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists')
    # The function ensures that there is no existing similar email
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email already exists')

# The login form for already registered users
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_password = BooleanField('Remember password')
    submit = SubmitField('Log in')

# Form used for adding products
Products_available = [("T-shirts"), ("Trousers"), ("Watches"), ("Shoes"), ("Shirt"), ("Socks"), ("Tie"), ("Belt"), ('Bag'), ('Scarf'), ('Jacket')]
class ProductForm(FlaskForm):
    product_name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg','png'])])
    price = StringField('Price', validators=[DataRequired()])
    product_type = SelectField('product_type', choices=Products_available, validators=[DataRequired()])
    submit = SubmitField('Add to Products')

class Purchasing(FlaskForm):
    numberOfItems = IntegerField('Quantity', validators=[DataRequired()]) 
    submit = SubmitField('Buy Now')

# Form for updating the profile
class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    picture = FileField('Chose Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update Profile')


    # The function ensures that there is no existing similar user name
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists')
    # The function ensures that there is no existing similar email
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('Email already exists')


# Search form 
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')