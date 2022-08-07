CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT,
    role INTEGER
);

CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    name TEXT,
    visible INTEGER
);

CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER REFERENCES decks,
    word1 TEXT,
    word2 TEXT
);

CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    card_id INTEGER REFERENCES cards,
    sent_at TIMESTAMP,
    result INTEGER
);
