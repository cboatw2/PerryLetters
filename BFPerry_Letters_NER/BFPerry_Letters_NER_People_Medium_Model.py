import spacy
from pathlib import Path

# Load medium English model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("Model 'en_core_web_md' not installed. Install with:")
    print("    python3 -m spacy download en_core_web_md")
    exit(1)

input_folder = Path("/Users/crboatwright/PerryLetters/BFPerryLettersSeparated")
output_file = Path("/Users/crboatwright/PerryLetters/BFPerry_Letters_NER/PeopleOnlyMediumModel.txt")

# Collect all persons from all letter files
all_persons = set()

# Loop over all .txt files in the folder
for letter_file in sorted(input_folder.glob("*.txt")):
    text = letter_file.read_text(encoding="utf-8", errors="ignore")
    doc = nlp(text)
    
    # Extract only PERSON entities from this letter
    persons = {ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"}
    all_persons.update(persons)
    
    print(f"Processed {letter_file.name}: found {len(persons)} unique persons")

# Write results
with output_file.open("w", encoding="utf-8") as out:
    out.write(f"=== PERSON entities from {input_folder.name} folder (en_core_web_md) ===\n\n")
    for name in sorted(all_persons):
        out.write(name + "\n")

print(f"\nWrote {len(all_persons)} total unique PERSON entities to {output_file}")