import re

input_file = "BFPerryTranscribedLetters.txt"
output_file = "BFPerryLetters_split.txt"

# Regex for start of letter (day/date line)
start_re = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[^a-zA-Z0-9]*.*', re.IGNORECASE)
# Regex for end of letter (recipient name and place)
end_re = re.compile(r'^Mrs\. Elizabeth Perry|^Miss Anna Perry|^Mr\. W\.H\.M\. Perry|^William Perry', re.IGNORECASE)

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

letters = []
current_letter = []
in_letter = False

for line in lines:
    # Detect start of a letter
    if start_re.match(line.strip()):
        if current_letter:
            letters.append("".join(current_letter))
            current_letter = []
        in_letter = True
    if in_letter:
        current_letter.append(line)
    # Detect end of a letter
    if in_letter and end_re.match(line.strip()):
        current_letter.append("\n")
        letters.append("".join(current_letter))
        current_letter = []
        in_letter = False

# Save letters to output file, separated by delimiter
with open(output_file, "w", encoding="utf-8") as out:
    for i, letter in enumerate(letters, 1):
        out.write(f"=== Letter {i} ===\n")
        out.write(letter)
        out.write("\n")

print(f"Saved {len(letters)} letters to {output_file}")