import os
import re
import csv
import sqlite3
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Connect to database
conn = sqlite3.connect("BFPerryLetters.db")
cur = conn.cursor()

letters_dir = "BFPerryLettersSeparated"
output_csv = "BFPerryLetters_metadata.csv"

def extract_metadata(text, filename):
    # Letter number from filename
    letter_number = int(re.search(r'Letter(\d+)', filename).group(1))
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Date: look for a line with a date pattern near the top
    date = ""
    for line in lines[:5]:
        match = re.search(r'(\d{1,2} [A-Za-z]+ \[?\d{4}\]?|[A-Za-z]+ morning, \d{1,2} [A-Za-z]+ \[?\d{4}\]?)', line)
        if match:
            date = match.group(0)
            break
    
    # Sent from location: last non-empty line
    sent_from = lines[-1] if lines else ""
    
    # Recipient: second-to-last non-empty line
    recipient = lines[-2] if len(lines) > 1 else ""
    
    # Sender: look for "Yours, ..." or "B.F. Perry" in last 10 lines
    sender = ""
    for line in lines[-10:]:
        match = re.search(r'(B\.F\. Perry|Benjamin Franklin Perry|Yours.*)', line)
        if match:
            sender = match.group(0)
            break
    
    return [letter_number, date, sent_from, recipient, sender, filename]

# Write metadata to CSV
with open(output_csv, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["letter_number", "date", "sent_from", "recipient", "sender", "filename"])
    for filename in os.listdir(letters_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(letters_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            metadata = extract_metadata(text, filename)
            writer.writerow(metadata)

print(f"Metadata extracted to {output_csv}")

conn.commit()
conn.close()

csv_file = "BFPerryLetters_metadata.csv"

# Read the original metadata
with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# Insert new column after sent_from
sent_from_index = header.index("sent_from")
header.insert(sent_from_index + 1, "sent_to_location")

for row in rows:
    filename = row[-1]
    letter_path = os.path.join(letters_dir, filename)
    sent_to_location = ""
    if os.path.exists(letter_path):
        with open(letter_path, "r", encoding="utf-8") as lf:
            lines = [line.strip() for line in lf if line.strip()]
            if lines:
                sent_to_location = lines[-1]
    row.insert(sent_from_index + 1, sent_to_location)

# Sort by letter_number (convert to int, handle missing/empty values)
rows.sort(key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'))

# Overwrite the original CSV
with open(csv_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Overwritten {csv_file} with sent_to_location and sorted by letter number.")