import re
import os

# Path to the source file
source_file = "BFPerryLetters_split.txt"

# Output directory for individual letters
output_dir = "BFPerryLettersSeparated"
os.makedirs(output_dir, exist_ok=True)

# Read the entire file
with open(source_file, "r", encoding="utf-8") as f:
    text = f.read()

# Regex to match each letter header and its content
letter_pattern = re.compile(
    r"(Letter (\d+)[\s\S]*?)(?=Letter \d+|$)", re.MULTILINE
)

# Find all letters
letters = letter_pattern.findall(text)

for letter_content, letter_number in letters:
    filename = f"BFPerry_Letter{letter_number}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as out:
        out.write(letter_content.strip())

print(f"Saved {len(letters)} letters")