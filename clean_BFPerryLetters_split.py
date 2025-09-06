input_file = "BFPerryLetters_split.txt"
output_file = "BFPerryLetters_split_cleaned.txt"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

cleaned_lines = []
previous_blank = False

for line in lines:
    # Remove lines that are only whitespace
    if line.strip() == "":
        if not previous_blank:
            cleaned_lines.append("\n")  # Keep only one blank line in a row
        previous_blank = True
    else:
        cleaned_lines.append(line.rstrip() + "\n")
        previous_blank = False

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print(f"Extra spaces removed. Cleaned file saved as {output_file}.")