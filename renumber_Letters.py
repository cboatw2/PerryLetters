import re

input_file = "BFPerryLetters_split.txt"

# Read the file
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

letter_pattern = re.compile(r"^(Letter )(\d+)\b")
current_number = 1
used_numbers = set()
output_lines = []

for line in lines:
    match = letter_pattern.match(line)
    if match:
        # If this number has already been used, increment until unique
        while current_number in used_numbers:
            current_number += 1
        # Replace with the next available number
        new_line = f"Letter {current_number}\n"
        output_lines.append(new_line)
        used_numbers.add(current_number)
        current_number += 1
    else:
        output_lines.append(line)

# Overwrite the original file
with open(input_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print("Duplicate letter numbers fixed and file renumbered.")