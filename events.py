from random import randint
from flask import render_template
from sqlalchemy import false, null
from db import db

def get_event(name):
    sql = "SELECT EXISTS(SELECT life FROM events WHERE word2=:name)"
    result = db.session.execute(sql, {"name":name}).fetchone()[0]
    if result == 0:
        return "Not found"
    sql = "SELECT life FROM events WHERE word2=:name"
    result = db.session.execute(sql, {"name":name}).fetchone()[0]
    return result

def get_all_events():
    sql = "SELECT word2 FROM events ORDER BY word2 ASC"
    return db.session.execute(sql).fetchall()

def add_event(name, event):
    sql = """INSERT INTO events (word2, life)
                 VALUES (:word2, :life)"""
    db.session.execute(sql, {"word2":name, "life":event})
    db.session.commit()

