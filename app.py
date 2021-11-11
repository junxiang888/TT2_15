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
    
    
    def __repr__(self):
        return f"User('{self.id}','{self.username}', '{self.password_hash}', '{self.name}', '{self.appointment}')"



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


class LoginForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length( min=3,
        max = 20)] , render_kw = {"placeholder" : "Username"})


    password = PasswordField(validators = [InputRequired(), Length( min=3,
        max = 20)] , render_kw = {"placeholder" : "Password"})

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length( min=3,
        max = 20)] , render_kw = {"placeholder" : "Username"})


    password = PasswordField(validators = [InputRequired(), Length( min=3,
        max = 20)] , render_kw = {"placeholder" : "Password"})

    submit = SubmitField("Register")


    def validate_username(self,username):
        existing_username = User.query.filter_by(
            username = username.data).first()

        if existing_username:
            raise ValidationError(
                "That username already exists. Please choose another name")




@ app.route('/', methods = ['GET','POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()

        if user:

            if bcrypt.check_password_hash(user.password_hash, form.password.data):
                print("correct password")
                login_user(user)
                return redirect(url_for('dashboard_page'))

    return render_template('loginPage.html' , form = form)




@ app.route('/register' , methods = ['GET','POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user_name_input = request.form['register_name']
        user_appointment_input = request.form['register_appointment']
        new_user = User(username= form.username.data, 
            password_hash = hashed_password,
            name =  user_name_input,
            appointment = user_appointment_input
            )
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login_page'))
    
    return render_template('registrationPage.html' , form = form)




@ app.route('/dashboard_page', methods = ['GET','POST'])
def dashboard_page():
    current_user_obj = User.query.filter_by(username = current_user.username).first()

    current_user_proj_obj = Project.query.filter_by(user_id = current_user_obj.id ).all()

    return render_template('dashBoard.html' , user_projects = current_user_proj_obj )







@ app.route('/add_new_project', methods = ['GET','POST'])
@login_required
def add_project():
    
    return render_template('add_project.html' )



@ app.route('/add_new_project_api', methods = ['GET','POST'])
@login_required
def add_project_api():
    user_input_name = request.form['input_name']    
    user_input_description = request.form['input_description']
    user_input_budget = request.form['input_budget']

    user = User.query.filter_by(username = current_user.username).first()

    
    new_project_obj  = Project(
                name = user_input_name,
                description = user_input_description,
                budget = user_input_budget,
                user_id = user.id
        )
    db.session.add(new_project_obj)
    db.session.commit()

    return redirect(url_for('dashboard_page') )


@app.route('/logout', methods = ['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/project_details', methods = ['GET','POST'])
@login_required
def project_details():
    user = User.query.filter_by(username = current_user.username).first()
    current_user_id = user.id 
    project_id = Project.query.filter_by(user_id = current_user_id).first()
    current_project_id = project_id.id
    expense_object = Expense.query.filter_by(project_id = current_project_id)

    return render_template('projectDashBoard.html' , expense_obj = expense_object)


@app.route('/delete_project/<int:project_id>' )
def delete_project(project_id):

    user_project_query = Project.query.filter_by(id = project_id ).first()
    db.session.delete(user_project_query)
    db.session.commit()
    return redirect(url_for('dashboard_page'))

@app.route('/edit_project/<int:project_id>')
def edit_expense(project_id):
    return redirect(url_for('project_page'))
    
@app.route('/add_new_expense', methods = ['GET','POST'])
@login_required
def add_expense():
    
    return render_template('add_expense.html' )
    #front end adding

@ app.route('/add_new_expense_api', methods = ['GET','POST'])
@login_required
def add_expenses_api():
    user_input_name = request.form['input_name']    
    user_input_description = request.form['input_description']
    user_input_amount = request.form['input_amount']
    time_now = datetime.today()
    new_created_at = time_now.strftime("%B %d, %Y")

    project = Expense.query.filter_by(id = current_user).first()
    #how to get the project ? Do am i able to use Current_project?
    new_expense_obj  = Project(
                name = user_input_name,
                description = user_input_description,
                amont = user_input_amount,
                created_at = new_created_at,
                update_at = new_created_at,
                project_id = project.id,
                category_id = 1
        )
    db.session.add(new_expense_obj)
    db.session.commit()
    return redirect(url_for('project_page') )

@app.route('/delete_expense/<int:expense_id>' )
def delete_expense(expense_id):
    user_expense_query = Expense.query.filter_by(id = expense_id ).first()
    db.session.delete(user_expense_query)
    db.session.commit()
    return redirect(url_for('project_page'))

if __name__ == '__main__':
	app.run(debug = True)



