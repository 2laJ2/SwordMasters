from random import randint

from flask import render_template
from sqlalchemy import false, null
from db import db

def get_all_decks():
    sql = "SELECT id, name FROM decks WHERE visible=1 ORDER BY name"
    return db.session.execute(sql).fetchall()

def get_deck_info(deck_id):
    sql = """SELECT d.name, u.username FROM decks d, users u
             WHERE d.id=:deck_id AND d.creator_id=u.id"""
    return db.session.execute(sql, {"deck_id": deck_id}).fetchone()

def get_deck_size(deck_id):
    sql = "SELECT COUNT(*) FROM cards WHERE deck_id = :deck_id"
    return db.session.execute(sql, {"deck_id": deck_id}).fetchone()[0]

def get_my_decks(user_id):
    sql = """SELECT id, name FROM decks
             WHERE creator_id=:user_id AND visible=1 ORDER BY name"""
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def add_deck(name, words, creator_id):
    sql = """INSERT INTO decks (creator_id, name, visible)
             VALUES (:creator_id, :name, 1) RETURNING id"""
    deck_id = db.session.execute(sql, {"creator_id":creator_id, "name":name}).fetchone()[0]

    for pair in words.split("\n"):
        parts = pair.strip().split(";")
        if len(parts) != 2:
            continue

        sql = """INSERT INTO cards (deck_id, word1, word2)
                 VALUES (:deck_id, :word1, :word2)"""
        db.session.execute(sql, {"deck_id":deck_id, "word1":parts[0], "word2":parts[1]})

    db.session.commit()
    return deck_id

def remove_deck(deck_id, user_id):
    sql = "UPDATE decks SET visible=0 WHERE id=:id AND creator_id=:user_id"
    db.session.execute(sql, {"id":deck_id, "user_id":user_id})
    db.session.commit()

def get_random_card(deck_id):
    size = get_deck_size(deck_id)
    pos = randint(0, size-1)
    sql = "SELECT id, word1 FROM cards WHERE deck_id=:deck_id LIMIT 1 OFFSET :pos"
    return db.session.execute(sql, {"deck_id":deck_id, "pos":pos}).fetchone()

def get_card_words(card_id):
    sql = "SELECT word1, word2 FROM cards WHERE id=:card_id"
    return db.session.execute(sql, {"card_id":card_id}).fetchone()

def send_answer(card_id, answer, user_id):
    sql = "SELECT word2 FROM cards WHERE id=:id"
    correct = db.session.execute(sql, {"id":card_id}).fetchone()[0]
    result = 1 if answer == correct else 0

    sql = """INSERT INTO answers (user_id, card_id, sent_at, result)
             VALUES (:user_id, :card_id, NOW(), :result)"""
    db.session.execute(sql, {"user_id":user_id, "card_id":card_id, "result":result})
    db.session.commit()

def get_event(name):
    sql = "SELECT EXISTS(SELECT life FROM events WHERE word2=:name)"
    result = db.session.execute(sql, {"name":name}).fetchone()[0]
    if result == 0:
        return "Not found"
    sql = "SELECT life FROM events WHERE word2=:name"
    result = db.session.execute(sql, {"name":name}).fetchone()[0]
    return result

def add_event(name, event):
    sql = """INSERT INTO events (word2, life)
                 VALUES (:word2, :life)"""
    db.session.execute(sql, {"word2":name, "life":event})
    db.session.commit()
