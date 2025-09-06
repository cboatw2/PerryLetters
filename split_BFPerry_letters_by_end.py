import re

input_file = "BFPerryTranscribedLetters.txt"
output_file = "BFPerryLetters_split.txt"

# Pattern for letter ending: recipient name and location (e.g., Mrs. Elizabeth Perry\nGreenville)
end_re = re.compile(
    r"^(Mrs\.|Miss|Mr\.|William|Anna|Benjamin|Elizabeth|W\.H\.M\.)\s[\w\.\s]+[\r\n]+(Greenville|Columbia|Laurens C\.H\.|Anderson|Spartanburgh C\.H\.|Water Loo P\.O\.|Kinder Hook|Boston|Albany|New Haven|Philadelphia|Washington|Charleston|Pickens C\.H\.)",
    re.IGNORECASE
)

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

letters = []
current_letter = []

for i, line in enumerate(lines):
    current_letter.append(line)
    # Check for end of letter
    if i < len(lines) - 1:
        # Look ahead to next line for location
        next_line = lines[i + 1].strip()
        combined = line.strip() + "\n" + next_line
        if end_re.match(combined):
            current_letter.append(lines[i + 1])
            letters.append("".join(current_letter).strip())
            current_letter = []
    else:
        # Last line
        if current_letter:
            letters.append("".join(current_letter).strip())

# Save letters to output file, separated by delimiter
with open(output_file, "w", encoding="utf-8") as out:
    for i, letter in enumerate(letters, 1):
        out.write(f"=== Letter {i} ===\n")
        out.write(letter)
        out.write("\n\n")

print(f"Saved {len(letters)} letters to {output_file}")