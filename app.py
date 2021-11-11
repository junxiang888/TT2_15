from app import app
import json
import flask

category = json.load(open('category.json'))
expense = json.load(open('expense.json'))
project = json.load(open('project.json'))
user = json.load(open('user.json'))
