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

# Pattern to match letter start (day of week followed by date)
# Matches patterns like "Thursday night, 30 November [1837]"
start_pattern = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', re.IGNORECASE)

# Pattern to match letter end (name followed by city)
# Matches patterns like "Benjamin Perry\nColumbia" or similar
end_pattern = re.compile(r'^[A-Z][a-z]+ [A-Z][a-z]+\s*$')

letters = []
current_letter = []
in_letter = False

for i, line in enumerate(content_lines):
    # Check if this is the start of a new letter
    if start_pattern.match(line.strip()):
        # If we were already building a letter, save it
        if current_letter:
            letters.append(''.join(current_letter))
            current_letter = []
        in_letter = True
        current_letter.append(line)
    elif in_letter:
        current_letter.append(line)
        
        # Check if this might be the end (person's name)
        if end_pattern.match(line.strip()):
            # Look ahead for city name
            if i + 1 < len(content_lines):
                next_line = content_lines[i + 1].strip()
                # If next line looks like a city name (capitalized word(s))
                if next_line and next_line[0].isupper():
                    current_letter.append(content_lines[i + 1])
                    letters.append(''.join(current_letter))
                    current_letter = []
                    in_letter = False

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