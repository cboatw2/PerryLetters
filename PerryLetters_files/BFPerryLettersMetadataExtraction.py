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
    
    # Date: find the first line with a date pattern
    date = ""
    date_index = None
    for idx, line in enumerate(lines):
        match = re.search(r'(\d{1,2} [A-Za-z]+ \d{4}|[A-Za-z]+ morning, \d{1,2} [A-Za-z]+ \d{4}|[A-Za-z]+, \d{1,2} [A-Za-z]+ \d{4})', line)
        if match:
            date = match.group(0)
            date_index = idx
            break
    
    # Sent from: line immediately after the date line
    sent_from = ""
    if date_index is not None and date_index + 1 < len(lines):
        sent_from = lines[date_index + 1]
    
    # Sent to location: last non-empty line
    sent_to_location = lines[-1] if lines else ""
    
    # Recipient: second-to-last non-empty line
    recipient = lines[-2] if len(lines) > 1 else ""
    
    # Sender: look for "B.F. Perry" or similar in last 10 lines
    sender = ""
    for line in lines[-10:]:
        match = re.search(r'(B\.F\. Perry|Benjamin Franklin Perry|Yours.*)', line)
        if match:
            sender = match.group(0)
            break
    
    return [letter_number, date, sent_from, sent_to_location, recipient, sender, filename]

# Write metadata to CSV
with open(output_csv, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["letter_number", "date", "sent_from", "sent_to_location", "recipient", "sender", "filename"])
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

# Remove the old sent_to_location column if it exists
if header.count("sent_to_location") > 1:
    # Remove all but the first occurrence
    first_index = header.index("sent_to_location")
    # Remove extra columns from header
    header = [col for i, col in enumerate(header) if col != "sent_to_location" or i == first_index]
    # Remove extra columns from rows
    for i, row in enumerate(rows):
        new_row = []
        sent_to_count = 0
        for j, val in enumerate(row):
            if header[j] == "sent_to_location":
                sent_to_count += 1
                if sent_to_count > 1:
                    continue
            new_row.append(val)
        rows[i] = new_row

# Update sent_to_location values
sent_to_index = header.index("sent_to_location")
for row in rows:
    filename = row[-1]
    letter_path = os.path.join(letters_dir, filename)
    sent_to_location = ""
    if os.path.exists(letter_path):
        with open(letter_path, "r", encoding="utf-8") as lf:
            lines = [line.strip() for line in lf if line.strip()]
            if lines:
                sent_to_location = lines[-1]
    row[sent_to_index] = sent_to_location

# Overwrite the original CSV
with open(csv_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Overwritten {csv_file} with a single sent_to_location column.")

# Sort the CSV by letter_number
import csv

csv_file = "BFPerryLetters_metadata.csv"
sorted_csv_file = "BFPerryLetters_metadata.csv"  # Overwrite the same file

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# Sort rows by letter_number (convert to int, handle missing/empty values)
rows.sort(key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'))

with open(sorted_csv_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Sorted {csv_file} by letter_number.")