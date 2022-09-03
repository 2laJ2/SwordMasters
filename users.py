import os
from db import db
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash

def create_user(username, password1, role):
    hash_value = generate_password_hash(password1)
    sql = "INSERT INTO users (username, password, role) VALUES (:username, :password, :role)"
    db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
    db.session.commit()
    session["username"] = username
    newuser = check_username(username)
    if not newuser or len(newuser) != 3:
        return False
    session["user_id"] = newuser[0]
    session["user_role"] = newuser[2]
    session["csrf_token"] = os.urandom(16).hex()
    return True

def check_username(username):
    sql = "SELECT id, password, role FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    return user

def user_id():
    return session.get("user_id", 0)

def require_role(role):
    if role > session.get("user_role", 0):
        abort(403)

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)