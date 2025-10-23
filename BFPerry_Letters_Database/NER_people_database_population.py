import sqlite3
import csv

db_file = "BFPerryLetters.db"
csv_file = "BFPerry_Letters_NER/BFPerryLetters_NER_final.csv"  # Updated path

conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Create the people table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS people (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

people_set = set()

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["entity_type"] == "PERSON":
            name = row["entity_name"].strip()
            if name and name not in people_set:
                cur.execute("INSERT OR IGNORE INTO people (name) VALUES (?)", (name,))
                people_set.add(name)

conn.commit()
conn.close()

print(f"Loaded unique PERSON entities into people table in {db_file}.")