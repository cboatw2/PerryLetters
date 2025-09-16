import sqlite3
import csv

db_file = "BFPerryLetters.db"
csv_file = "BFPerry_Letters_NER/BFPerry_NER_entities_fixed_3.csv"

conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Make sure the mentioned_people table exists
cur.execute("""
CREATE TABLE IF NOT EXISTS mentioned_people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_id INTEGER,
    person_id INTEGER,
    FOREIGN KEY(letter_id) REFERENCES letter(id),
    FOREIGN KEY(person_id) REFERENCES people(person_id)
)
""")

def get_letter_id(letter_number):
    cur.execute("SELECT id FROM letter WHERE letter_number=?", (letter_number,))
    result = cur.fetchone()
    return result[0] if result else None

def get_person_id(person_name):
    cur.execute("SELECT person_id FROM people WHERE name=?", (person_name,))
    result = cur.fetchone()
    return result[0] if result else None

def get_sender_recipient_ids(letter_id):
    cur.execute("SELECT sender_id, recipient_id FROM letter WHERE id=?", (letter_id,))
    result = cur.fetchone()
    if result:
        return set([x for x in result if x is not None])
    return set()

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["entity_type"] == "PERSON":
            letter_number = row["letter_number"].strip()
            person_name = row["entity_name"].strip()
            letter_id = get_letter_id(letter_number)
            person_id = get_person_id(person_name)
            if letter_id and person_id:
                sender_recipient_ids = get_sender_recipient_ids(letter_id)
                # Only insert if not sender or recipient
                if person_id not in sender_recipient_ids:
                    cur.execute("""
                        INSERT OR IGNORE INTO mentioned_people (letter_id, person_id)
                        VALUES (?, ?)
                    """, (letter_id, person_id))

conn.commit()
conn.close()

print("Mentioned people (excluding sender/recipient) loaded into mentioned_people table.")