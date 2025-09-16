import sqlite3
import csv

db_file = "BFPerryLetters.db"
csv_file = "BFPerry_Letters_NER/BFPerry_NER_entities_fixed_3.csv"

conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Create the location table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS location (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    latitude REAL,
    longitude REAL
)
""")

location_set = set()

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["entity_type"] == "LOCATION":
            name = row["entity_name"].strip()
            if name and name not in location_set:
                cur.execute("INSERT OR IGNORE INTO location (name) VALUES (?)", (name,))
                location_set.add(name)

conn.commit()
conn.close()

print(f"Loaded unique LOCATION entities into location table in {db_file}.")