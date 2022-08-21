from db import db

def get_deck_stats(deck_id, user_id):
    sql = """SELECT COUNT(*), COALESCE(SUM(a.result),0) FROM answers a, cards c
             WHERE c.deck_id=:deck_id AND a.user_id=:user_id AND a.card_id=c.id"""
    return db.session.execute(sql, {"deck_id":deck_id, "user_id":user_id}).fetchone()

def get_full_stats(user_id):
    sql = """SELECT id, name FROM decks
             WHERE creator_id=:user_id AND visible=1 ORDER BY name"""
    decks = db.session.execute(sql, {"user_id": user_id}).fetchall()

    data = []
    for deck in decks:
        sql = """SELECT u.username, COUNT(*), COALESCE(SUM(a.result),0)
                 FROM answers a, cards c, users u
                 WHERE c.deck_id=:deck_id AND a.card_id=c.id AND u.id=a.user_id
                 GROUP BY u.id, u.username ORDER BY u.username"""
        results = db.session.execute(sql, {"deck_id": deck[0]}).fetchall()
        data.append((deck[1], results))

    return data