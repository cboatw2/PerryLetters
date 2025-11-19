import re

input_file = "BFPerryTranscribedLetters.txt"
output_file = "BFPerryLetters_split.txt"

# Patterns for end and start of letters
location_pattern = re.compile(r"^(.*?)(Greenville|Columbia|Laurens C\.H\.|Anderson|Spartanburgh C\.H\.|Water Loo P\.O\.|Kinder Hook|Boston|Albany|New Haven|Philadelphia|Washington|Charleston|Pickens C\.H\.|Sans Souci)[ \t]*$", re.IGNORECASE)
date_pattern = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|[0-9]{1,2} [A-Za-z]+ [0-9]{4}|[A-Za-z]+, [0-9]{1,2} [A-Za-z]+ [0-9]{4}|[0-9]{1,2} [A-Za-z]+|[A-Za-z]+ [0-9]{4}|[A-Za-z]+, [0-9]{4}|[0-9]{4})", re.IGNORECASE)

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

letters = []
current_letter = []
letter_count = 1
i = 0
while i < len(lines):
    current_letter.append(lines[i])
    # Check for end of letter (location line)
    if location_pattern.match(lines[i].strip()):
        # Look ahead for start of next letter (date/day line)
        j = i + 1
        while j < len(lines):
            if date_pattern.match(lines[j].strip()):
                # Insert header before the next letter
                letters.append("".join(current_letter).strip())
                current_letter = []
                break
            current_letter.append(lines[j])
            j += 1
        i = j
    else:
        i += 1

# Add any remaining text as the last letter
if current_letter:
    letters.append("".join(current_letter).strip())

# Write output with headers
with open(output_file, "w", encoding="utf-8") as out:
    for idx, letter in enumerate(letters, 1):
        out.write(f"Letter {idx}\n")
        out.write(letter)
        out.write("\n\n")

print(f"Split into {len(letters)} letters and saved to {output_file}")