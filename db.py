from os import getenv
from app import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)