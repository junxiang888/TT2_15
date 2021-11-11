from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin , login_user , LoginManager, login_required, logout_user, current_user
from flask import Flask, render_template, url_for, redirect , request

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import sys
import requests
from flask_restful import Api, Resource , reqparse, abort,  fields, marshal_with

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func



app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///templates/database.db'


app.config['SECRET_KEY'] = 'thisisasecretkey'


BASE = "http://127.0.0.1:5000/"


api = Api(app)




login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(128))
    appointment = db.Column(db.String(128))
    user_id = db.Column(db.String(128))
    
    def __repr__(self):
        return f"User('{self.id}','{self.username}', '{self.password_hash}', '{self.name}', '{self.appointment}')"




class LoginForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length( min=3,
        max = 20)] , render_kw = {"placeholder" : "Username"})


    password = PasswordField(validators = [InputRequired(), Length( min=3,
        max = 20)] , render_kw = {"placeholder" : "Password"})

    submit = SubmitField("Login")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable = False )
    description = db.Column(db.String(200),nullable = True)
    budget = db.Column(db.Float(100), nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.id}','{self.name}', '{self.description}', '{self.budget}', '{self.user_id}')"

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.id}','{self.name}', '{self.description}', '{self.amount}', '{self.created_at}', '{self.update_at}', '{self.project_id}', '{self.category_id}')"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Post('{self.id}','{self.name}')"




@ app.route('/', methods = ['GET','POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))

    return render_template('loginPage.html' , form = form)


if __name__ == '__main__':
	app.run(debug = True)



