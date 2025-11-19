import os
import re

source_file = "BFPerryLetters_split_cleaned.txt"
output_dir = "BFPerryLettersSeparated"
os.makedirs(output_dir, exist_ok=True)

with open(source_file, "r", encoding="utf-8") as f:
    text = f.read()

# Split by "Letter N" headers, keeping the header with each letter
parts = re.split(r"(Letter \d+)", text)
letters = []
for i in range(1, len(parts), 2):
    header = parts[i].strip()
    content = parts[i+1].strip() if i+1 < len(parts) else ""
    letter_text = f"{header}\n{content}"
    letters.append(letter_text)

for idx, letter_content in enumerate(letters, 1):
    filename = f"BFPerry_Letter{idx}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as out:
        out.write(letter_content.strip())

print(f"Saved {len(letters)} letters")