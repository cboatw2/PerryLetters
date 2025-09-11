import spacy
import csv
import os
import re

nlp = spacy.load("en_core_web_sm")
letters_dir = "BFPerryLettersSeparated"

entities = []

for filename in os.listdir(letters_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(letters_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        # Extract letter number from filename only
        letter_number_match = re.search(r'BFPerry_Letter(\d+)\.txt', filename)
        letter_number = letter_number_match.group(1) if letter_number_match else ""
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities.append([letter_number, ent.text.strip(), "PERSON"])
            elif ent.label_ == "GPE":
                entities.append([letter_number, ent.text.strip(), "LOCATION"])

# Overwrite the CSV with new results
with open("BFPerry_NER_entities.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["letter_number", "entity_name", "entity_type"])
    writer.writerows(entities)

print("Saved entities to BFPerry_NER_entities.csv")
