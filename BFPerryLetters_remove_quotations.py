input_file = "BFPerry_NER_entities.csv"
output_file = "BFPerry_NER_entities_cleaned.csv"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

cleaned_lines = [line.replace('"', '') for line in lines]

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print(f'All double quotes removed and saved to {output_file}.')