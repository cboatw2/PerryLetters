import csv
import re

def normalize_entity(entity):
    # Remove leading/trailing whitespace
    entity = entity.strip()
    # Replace multiple spaces with single space
    entity = re.sub(r'\s+', ' ', entity)
    # Add periods between initials (e.g., "B F Perry" -> "B. F. Perry")
    entity = re.sub(r'\b([A-Z])\b', r'\1.', entity)
    # Remove extra periods (e.g., "B.. F.. Perry" -> "B. F. Perry")
    entity = re.sub(r'\.{2,}', '.', entity)
    # Remove spaces before periods
    entity = re.sub(r'\s+\.', '.', entity)
    # Remove spaces after periods
    entity = re.sub(r'\.\s+', '. ', entity)
    # Remove stray commas, semicolons, etc. at ends
    entity = entity.strip(' ,;:.')
    return entity

def is_junk(entity):
    # Too short
    if len(entity) <= 2:
        return True
    # Only symbols or digits
    if re.match(r'^[^A-Za-z]+$', entity):
        return True
    # Obvious non-names (add more as needed)
    junk_words = {
        "Bananas", "Breakfast", "Lunch", "Dinner", "Gallery", "Grammar", "China", "America", "Equity",
        "Farms", "Fields", "Library", "Painting", "Resolutions", "States", "Town", "Home", "Ladies",
        "Parlor", "Schoolcraft", "Sugar", "Truly", "Wellborn Perry", "beaux", "bee��", "drank", "inkstand ivory",
        "ivory match box", "parlor ball", "strawberry pies", "mutton", "turkey", "well.", "ytoung"
    }
    # Remove if in junk list or only symbols
    if entity in junk_words:
        return True
    return False

input_file = "NER_long_table_deduped.csv"
output_file = "NER_long_table_cleaned.csv"

seen = set()
cleaned_rows = []

with open(input_file, "r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)
    cleaned_rows.append(header)
    for row in reader:
        year_range, entity, entity_type = row
        norm_entity = normalize_entity(entity)
        # Remove junk and deduplicate (case-insensitive)
        key = (year_range, norm_entity.lower(), entity_type)
        if not is_junk(norm_entity) and key not in seen:
            seen.add(key)
            cleaned_rows.append([year_range, norm_entity, entity_type])

with open(output_file, "w", encoding="utf-8", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerows(cleaned_rows)

print(f"Cleaned table saved as {output_file}")