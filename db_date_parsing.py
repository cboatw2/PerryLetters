import sqlite3
import re

db_file = "BFPerryLetters.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Regex to match (d)d month yyyy
date_pattern = re.compile(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$")

cur.execute("SELECT id, date FROM letter")
for row in cur.fetchall():
    letter_id, date_str = row
    if date_str:
        match = date_pattern.match(date_str.strip())
        if match:
            day, month, year = match.groups()
            cur.execute(
                "UPDATE letter SET day=?, month=?, year=? WHERE id=?",
                (day, month, year, letter_id)
            )

conn.commit()
conn.close()
print("Day, month, and year columns populated.")