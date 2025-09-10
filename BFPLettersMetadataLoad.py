import csv
import sqlite3

db_file = "BFPerryLetters.db"
csv_file = "BFPerryLetters_metadata.csv"

conn = sqlite3.connect(db_file)
cur = conn.cursor()

def get_or_create_person(name):
    cur.execute("INSERT OR IGNORE INTO people (name) VALUES (?)", (name,))
    cur.execute("SELECT person_id FROM people WHERE name=?", (name,))
    result = cur.fetchone()
    return result[0] if result else None

def get_or_create_location(name):
    cur.execute("INSERT OR IGNORE INTO location (name) VALUES (?)", (name,))
    cur.execute("SELECT location_id FROM location WHERE name=?", (name,))
    result = cur.fetchone()
    return result[0] if result else None

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        letter_number = int(row["letter_number"]) if row["letter_number"].isdigit() else None
        date = row["date"]
        file_path = row["filename"]

        # Get or create people and locations
        sender_id = get_or_create_person(row["sender"])
        recipient_id = get_or_create_person(row["recipient"])
        sent_from_id = get_or_create_location(row["sent_from"])
        sent_to_id = get_or_create_location(row["sent_to_location"])

        # Insert letter record
        cur.execute("""
            INSERT INTO letter (
                letter_number, date, sent_from_location_id, sent_to_location_id,
                sender_id, recipient_id, file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (letter_number, date, sent_from_id, sent_to_id, sender_id, recipient_id, file_path))

conn.commit()
conn.close()