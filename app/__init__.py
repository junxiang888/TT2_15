from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f9668b6e45f66487549fc7c385f063cf'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app) 
bcrypt = Bcrypt(app)
authtoken = 'f9668basdf2134664sdf345234asdc385f063cf'

from app import routes