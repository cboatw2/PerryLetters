import sqlite3
import csv

db_file = "BFPerryLetters.db"
csv_file = "BFPerry_Letters_NER/BFPerry_NER_entities_fixed_3.csv"

conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Make sure the mentioned_location table exists
cur.execute("""
CREATE TABLE IF NOT EXISTS mentioned_location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_id INTEGER,
    location_id INTEGER,
    FOREIGN KEY(letter_id) REFERENCES letter(id),
    FOREIGN KEY(location_id) REFERENCES location(location_id)
)
""")

def get_letter_id(letter_number):
    cur.execute("SELECT id FROM letter WHERE letter_number=?", (letter_number,))
    result = cur.fetchone()
    return result[0] if result else None

def get_location_id(location_name):
    cur.execute("SELECT location_id FROM location WHERE name=?", (location_name,))
    result = cur.fetchone()
    return result[0] if result else None

def get_sent_from_to_location_ids(letter_id):
    cur.execute("SELECT sent_from_location_id, sent_to_location_id FROM letter WHERE id=?", (letter_id,))
    result = cur.fetchone()
    if result:
        return set([x for x in result if x is not None])
    return set()

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["entity_type"] == "LOCATION":
            letter_number = row["letter_number"].strip()
            location_name = row["entity_name"].strip()
            letter_id = get_letter_id(letter_number)
            location_id = get_location_id(location_name)
            if letter_id and location_id:
                sent_from_to_ids = get_sent_from_to_location_ids(letter_id)
                # Only insert if not sent_from or sent_to
                if location_id not in sent_from_to_ids:
                    cur.execute("""
                        INSERT OR IGNORE INTO mentioned_location (letter_id, location_id)
                        VALUES (?, ?)
                    """, (letter_id, location_id))

conn.commit()
conn.close()

print("Mentioned locations (excluding sent_from/sent_to) loaded into mentioned_location table.")