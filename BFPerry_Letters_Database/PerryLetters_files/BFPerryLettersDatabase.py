import sqlite3

conn = sqlite3.connect("BFPerryLetters.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS people (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS location (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    latitude REAL,
    longitude REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS letter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_number INTEGER,
    date TEXT,
    sent_from_location_id INTEGER,
    sent_to_location_id INTEGER,
    sender_id INTEGER,
    recipient_id INTEGER,
    file_path TEXT,
    FOREIGN KEY(sent_from_location_id) REFERENCES location(location_id),
    FOREIGN KEY(sent_to_location_id) REFERENCES location(location_id),
    FOREIGN KEY(sender_id) REFERENCES people(person_id),
    FOREIGN KEY(recipient_id) REFERENCES people(person_id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS mentioned_location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_id INTEGER,
    location_id INTEGER,
    FOREIGN KEY(letter_id) REFERENCES letter(id),
    FOREIGN KEY(location_id) REFERENCES location(location_id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS mentioned_people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_id INTEGER,
    person_id INTEGER,
    FOREIGN KEY(letter_id) REFERENCES letter(id),
    FOREIGN KEY(person_id) REFERENCES people(person_id)
)
""")

#cur.execute("SELECT location_id FROM location WHERE name=?", (name,))

conn.commit()
conn.close()