import re
from pathlib import Path

# Set up paths
input_file = Path("/Users/crboatwright/PerryLetters/Elizabeths_Letters/EFMPerryTranscribedLetters.txt")
output_folder = Path("/Users/crboatwright/PerryLetters/Elizabeths_Letters/EFMPerry_Letters_split")

# Create output folder if it doesn't exist
output_folder.mkdir(exist_ok=True)

# Read the input file
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Skip first two lines
content_lines = lines[2:]

# Pattern to match letter start: day of week OR date format (DD Month YYYY)
# Matches "Thursday" or "30 November 1837" or "30 November [1837]"
day_pattern = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', re.IGNORECASE)
date_pattern = re.compile(r'^\d{1,2}\s+[A-Z][a-z]+\s+[\[\d]', re.IGNORECASE)

# Pattern to match signature (name followed by optional city)
# Name pattern: capitalized first and last name
name_pattern = re.compile(r'^[A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z][a-z]+\s*$|^[A-Z][a-z]+\s+[A-Z][a-z]+\s*$')

letters = []
current_letter = []
last_was_name = False
skip_next = False  # Flag to skip city line after adding it

for i, line in enumerate(content_lines):
    # Skip this line if it was already added as a city name
    if skip_next:
        skip_next = False
        continue
    
    stripped = line.strip()
    
    # Check if this line is a signature (name)
    is_name = name_pattern.match(stripped)
    
    # Check if this is the start of a NEW letter (not embedded within)
    # Only start new letter if we have a complete previous letter (ended with name)
    is_start = (day_pattern.match(stripped) or date_pattern.match(stripped))
    
    if is_start and last_was_name and current_letter:
        # We have a complete letter - save it
        letters.append(''.join(current_letter))
        current_letter = []
        last_was_name = False
    
    # Add line to current letter
    current_letter.append(line)
    
    # Track if this line was a name (potential end of letter)
    if is_name:
        # Check if next line is a city (capitalized, short line)
        # Also check for blank line followed by city
        city_line_idx = i + 1
        
        # Skip blank lines between name and city
        while city_line_idx < len(content_lines) and content_lines[city_line_idx].strip() == '':
            current_letter.append(content_lines[city_line_idx])
            city_line_idx += 1
        
        # Now check if we have a city name
        if city_line_idx < len(content_lines):
            next_line = content_lines[city_line_idx].strip()
            if next_line and len(next_line) < 30 and next_line[0].isupper() and not date_pattern.match(next_line) and not day_pattern.match(next_line):
                # Add the city line
                current_letter.append(content_lines[city_line_idx])
                last_was_name = True
                # Mark to skip this line when we get to it in the main loop
                if city_line_idx == i + 1:
                    skip_next = True

# Don't forget the last letter if there is one
if current_letter:
    letters.append(''.join(current_letter))

# Write each letter to a separate file
for idx, letter in enumerate(letters, start=1):
    output_file = output_folder / f"Letter_{idx}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Letter {idx}\n\n")
        f.write(letter)

print(f"Split {len(letters)} letters into separate files in {output_folder}")
print(f"Files saved: Letter_1.txt through Letter_{len(letters)}.txt")