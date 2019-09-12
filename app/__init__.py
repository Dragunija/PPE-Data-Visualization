from flask import Flask
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
bootstrap = Bootstrap(app)
mongo = PyMongo(app)

from app import routes

