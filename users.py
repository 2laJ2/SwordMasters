import os
from db import db
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash

def user_id():
    return session.get("user_id", 0)

def require_role(role):
    if role > session.get("user_role", 0):
        abort(403)

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)