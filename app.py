from app import app
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(128))
    appointment = db.Column(db.String(128))
    user_id = db.Column(db.String(128))
    
    def __repr__(self):
        return f"User('{self.id}','{self.username}', '{self.password_hash}', '{self.name}', '{self.appointment}')"
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable = False )
    description = db.Column(db.string(200),nullable = True)
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

