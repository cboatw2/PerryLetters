import spacy
import csv
import os
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Path to the split letters directory (relative to this script)
letters_dir = os.path.join(os.path.dirname(__file__), "efmperry_letters_split")

entities = []

# Check if directory exists
if not os.path.exists(letters_dir):
    print(f"Error: Directory not found: {letters_dir}")
    exit(1)

print(f"Processing letters from: {letters_dir}")

# Process each letter file
for filename in sorted(os.listdir(letters_dir)):
    if filename.endswith(".txt"):
        file_path = os.path.join(letters_dir, filename)
        
        print(f"Processing: {filename}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Extract letter number from filename
        # Adjust pattern based on your filename format (e.g., "letter_001.txt" or "EFMPerry_Letter1.txt")
        letter_number_match = re.search(r'(\d+)', filename)
        letter_number = letter_number_match.group(1) if letter_number_match else filename
        
        # Run NER on the letter text
        doc = nlp(text)
        
        # Extract PERSON and GPE (location) entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities.append([letter_number, ent.text.strip(), "PERSON"])
            elif ent.label_ == "GPE":
                entities.append([letter_number, ent.text.strip(), "LOCATION"])

print(f"\nExtracted {len(entities)} entities from {len([f for f in os.listdir(letters_dir) if f.endswith('.txt')])} letters")

# Save to CSV in the Elizabeths_Letters directory
output_file = os.path.join(os.path.dirname(__file__), "EFMPerry_NER_entities.csv")

with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["letter_number", "entity_name", "entity_type"])
    writer.writerows(entities)

print(f"Saved entities to: {output_file}")

# Print summary statistics
person_count = sum(1 for e in entities if e[2] == "PERSON")
location_count = sum(1 for e in entities if e[2] == "LOCATION")
print(f"\nSummary:")
print(f"  Persons: {person_count}")
print(f"  Locations: {location_count}")
print(f"  Total: {len(entities)}")