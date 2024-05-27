from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, RadioField, SelectField, IntegerField, DecimalField, SelectMultipleField
from wtforms.validators import InputRequired, EqualTo

class RegistrationForm(FlaskForm):
    user_id = StringField("Username:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm password:", validators=[InputRequired(), EqualTo("password")])
    owner = RadioField("Do you wish to create new shop? ", choices=["yes", "no"], default = "no")
    submit = SubmitField("Submit")

class Register_shopForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    address = StringField("Address", validators=[InputRequired()])
    open_time = StringField("Opening time:", validators=[InputRequired()])
    close_time = StringField("Closing time:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_id = StringField("Username:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class Modify_shopFrom(FlaskForm):
    name = StringField("Name:", validators=[InputRequired()])
    address = StringField("Address:", validators=[InputRequired()])
    open_time = StringField("Opening time:", validators=[InputRequired()])
    close_time = StringField("Closing time:", validators=[InputRequired()])
    description = StringField("Description: ")
    submit = SubmitField("Submit")

class Add_flowersForm(FlaskForm):
    name = SelectField("What flower do you wish to add?", choices=[])
    price = DecimalField("Price:", validators=[InputRequired()])
    quantity = IntegerField("Quantity:", default = 1)
    submit = SubmitField("Submit")

class New_flowerForm(FlaskForm):
    name = StringField("Flower:", validators=[InputRequired()])
    submit = SubmitField("Add flower")

class New_bouquetForm(FlaskForm):
    name = StringField("Name:", validators=[InputRequired()] )
    flowers = SelectMultipleField("Choose which flowers will your bouquet have", choices=[], validators=[InputRequired()])
    price = DecimalField("Price: ", validators=[InputRequired()])
    quantity = IntegerField("Quantity:", default = 1)
    submit = SubmitField("Add bouquet")

class Modify_bouquetForm(FlaskForm):
    quantity = IntegerField("Add to stock:", validators=[InputRequired()] )
    submit = SubmitField("Update stock")