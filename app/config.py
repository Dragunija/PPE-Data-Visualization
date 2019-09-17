import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "glasgowPPE2019"
    MONGO_URI = "mongodb://localhost:27017/ppeDatabase"