from app import app
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import users
import decks
import stats
from db import db
import os

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    role = 1
    # check username and password
    sql = "SELECT id, password, role FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if not user:
        # invalid username
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username, password, role) VALUES (:username, :password, :role)"
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
        session["username"] = username
        sql = "SELECT id, password, role FROM users WHERE username=:username"
        resultnewuser = db.session.execute(sql, {"username":username})
        newuser = resultnewuser.fetchone()
        session["user_id"] = newuser[0]
        session["user_role"] = newuser[2]
        session["crf_token"] = os.urandom(16).hex()
        return render_template("index.html")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
        # correct username and password
            session["username"] = username
            session["user_id"] = user[0]
            session["user_role"] = user[2]
            session["crf_token"] = os.urandom(16).hex()
            return render_template("index.html")
        else:
            # invalid password
            return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    del session["user_role"]     
    return redirect("/")

@app.route("/decklist")
def deck():
    return render_template("decklist.html", decks=decks.get_all_decks())

@app.route("/explore")
def explore():
    return render_template("explore.html")

@app.route("/add", methods=["get", "post"])
def add_deck():
    #users.require_role(2) # works!
    if request.method == "GET":
        return render_template("add.html")
    if request.method == "POST":
        #users.check_crsf()
        name = request.form["name"]
        if len(name) < 1 or len(name) >25:
            return render_template("error.html", message="The deck name should consist of 1-25 characters")
        words = request.form["words"]
        if len(words) > 10000:
            return render_template("error.html", message="The list is too long")
        deck_id = decks.add_deck(name, words, users.user_id())
        return redirect("/deck/"+str(deck_id))

@app.route("/remove", methods=["get", "post"])
def remove_deck():
    #users.require_role(2) # works!
    if request.method == "GET":
        my_decks = decks.get_my_decks(users.user_id())# user specific - deck creator may remove
        return render_template("remove.html", list=my_decks)
    if request.method == "POST":
        #users.check_csrf()
        if "deck" in request.form:
            deck = request.form["deck"]
            decks.remove_deck(deck, users.user_id())
        return redirect("/")

@app.route("/deck/<int:deck_id>")
def show_deck(deck_id):
    info = decks.get_deck_info(deck_id)
    size = decks.get_deck_size(deck_id)
    total, correct = stats.get_deck_stats(deck_id, users.user_id())
    return render_template("deck.html", id=deck_id, deck_id=deck_id, name=info[0], creator=info[1], size=size,
                           total=total, correct=correct)

@app.route("/play/<int:deck_id>")
def play(deck_id):
    return render_template("play.html", id=deck_id)

@app.route("/stats")
def show_stats():
    return render_template("play.html", id=session["user_id"])
