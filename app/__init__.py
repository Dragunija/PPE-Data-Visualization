from flask import Flask
from app import config
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config.from_object(config.Config)
bootstrap = Bootstrap(app)
mongo = PyMongo(app)

from app import routes

