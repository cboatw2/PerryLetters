import re
import os

source_file = "BFPerryLetters_split.txt"
output_dir = "BFPerryLettersSeparated"
os.makedirs(output_dir, exist_ok=True)

with open(source_file, "r", encoding="utf-8") as f:
    text = f.read()

# Improved regex: match "Letter N" and all content until next "Letter N" or EOF
letter_pattern = re.compile(
    r"(Letter \d+[\s\S]*?)(?=Letter \d+|$)", re.MULTILINE
)

letters = letter_pattern.findall(text)

for idx, letter_content in enumerate(letters, 1):
    filename = f"BFPerry_Letter{idx}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as out:
        out.write(letter_content.strip())

print(f"Saved {len(letters)} letters")