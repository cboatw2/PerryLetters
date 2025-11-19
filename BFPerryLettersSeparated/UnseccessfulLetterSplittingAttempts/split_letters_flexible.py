import re

input_file = "BFPerryTranscribedLetters.txt"
output_file = "BFPerryLetters_split.txt"

# Patterns for possible letter starts
date_re = re.compile(r"^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?\s*(morning|evening|night)?\,?\s*\[?\d{1,2}\s\w+\s\d{4}\]?|^\d{1,2}\s\w+\s\d{4}|^\[\d{1,2}\s\w+\s\d{4}\]|^\d{1,2}\s\w+\s\[\d{4}\]", re.IGNORECASE)
place_re = re.compile(r"^(Columbia|Greenville|Laurens C\.H\.|Anderson C\.H\.|Pickens C\.H\.|Newberry CH|Charleston|Spartanburgh C\.H\.|Kinder Hook|Boston|Albany|New Haven|Philadelphia|Washington|Water Loo P\.O\.)$", re.IGNORECASE)
greeting_re = re.compile(r"^(My dear|My Dear|My dear Liz|My dear daughter|My dear Son|My Dear Willey|My dear Wife|My dear Little Daughter|My dear Sir)", re.IGNORECASE)

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

letters = []
current_letter = []
in_letter = False

for i, line in enumerate(lines):
    # Check for start of a letter
    if (
        date_re.match(line.strip())
        or place_re.match(line.strip())
        or greeting_re.match(line.strip())
    ):
        # If already collecting, save previous letter
        if current_letter:
            letters.append("".join(current_letter).strip())
            current_letter = []
        in_letter = True
    if in_letter:
        current_letter.append(line)
# Add last letter
if current_letter:
    letters.append("".join(current_letter).strip())

# Save letters to output file, separated by delimiter
with open(output_file, "w", encoding="utf-8") as out:
    for i, letter in enumerate(letters, 1):
        out.write(f"=== Letter {i} ===\n")
        out.write(letter)
        out.write("\n\n")

print(f"Saved {len(letters)} letters to {output_file}")