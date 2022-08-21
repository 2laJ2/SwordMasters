from app import app
from flask import redirect, render_template, abort, request, session
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
    # check username and password
    sql = "SELECT id, password, role FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if not user or username == "":
        # invalid username
        return render_template("error.html", message="The user does not exist")
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
            return render_template("error.html", message="The username and password do not match")

@app.route("/register", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        role = request.form["role"]
        if len(username) < 5 or len(username) > 20 or len(password1) < 5 or len(password1) > 20:
            return render_template("error.html", message="The username and password must contain 5 - 20 characters")
        if password2 == "":
            return render_template("error.html", message="Please confirm your password")
        if password1 != password2:
            return render_template("error.html", message="Please confirm the password correctly")
        if role not in ("1", "2"):
            return render_template("error.html", message="User role unknown")
        # check username
        sql = "SELECT id, password, role FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()    
        if user:
        # invalid username
            return render_template("error.html", message="The username is already taken")
        hash_value = generate_password_hash(password1)
        sql = "INSERT INTO users (username, password, role) VALUES (:username, :password, :role)"
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
        session["username"] = username
        sql = "SELECT id, password, role FROM users WHERE username=:username"
        resultnewuser = db.session.execute(sql, {"username":username})
        newuser = resultnewuser.fetchone()
        if not newuser or len(newuser) != 3:
            return render_template("error.html", message="Registering unsuccessful")
        session["user_id"] = newuser[0]
        session["user_role"] = newuser[2]
        session["crf_token"] = os.urandom(16).hex()
        return render_template("index.html")       

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
    users.require_role(2)
    if request.method == "GET":
        return render_template("add.html", message="")
    if request.method == "POST":
        #users.check_crsf() # not working
        name = request.form["name"]
        if len(name) < 1 or len(name) >25:
            return render_template("error.html", message="The deck name should consist of 1-25 characters")
        words = request.form["words"]
        if len(words) < 3 or ";" not in words:
            return render_template("error.html", message="The deck must contain at least one card")
        if len(words) > 10000:
            return render_template("error.html", message="The list is too long")
        deck_id = decks.add_deck(name, words, users.user_id())
        return redirect("/deck/"+str(deck_id))

@app.route("/remove", methods=["get", "post"])
def remove_deck():
    users.require_role(2)
    if request.method == "GET":
        my_decks = decks.get_my_decks(users.user_id())# user specific - deck creator may remove
        return render_template("remove.html", list=my_decks)
    if request.method == "POST":
        #users.check_csrf() # not working
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
    users.require_role(1)
    card = decks.get_random_card(deck_id)
    info = decks.get_deck_info(deck_id)
    return render_template("play.html", deck_id=deck_id, card_id=card[0], question=card[1], name=info[0])

@app.route("/result", methods=["post"])
def result():
    users.require_role(1)
    #users.check_csrf() # not working
    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    info = decks.get_deck_info(deck_id) 
    answer = request.form["answer"].strip()
    decks.send_answer(card_id, answer, users.user_id())
    words = decks.get_card_words(card_id)
    return render_template("result.html", deck_id=deck_id, question=words[0],
                           answer=answer, correct=words[1], name=info[0])

@app.route("/event", methods=["post"])
def events():
    answer = request.form["answer"].strip()
    if answer == "":
        return redirect("/explore")
    info = decks.get_event(answer)
    return render_template("event.html", name=answer, info=info)

@app.route("/addevent")
def addevent():
    return render_template("newevent.html")

@app.route("/newevent", methods=["post"])
def newevent():
    users.require_role(2)
    name = request.form["name"]
    words = request.form["words"]
    if name == "" or words == "":
        return render_template("error.html", message="The name of the person or event or the story are missing")
    search = decks.get_event(name)
    if search != "Not found":
        return render_template("error.html", message="The name of the person or event is already taken")
    decks.add_event(name, words)
    return redirect("/explore")

@app.route("/stats")
def show_stats():
    users.require_role(2)
    data = stats.get_full_stats(users.user_id())
    return render_template("stats.html", data=data)
    #return render_template("error.html", message=data)#"This page is under construction")
