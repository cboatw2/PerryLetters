import csv
from pathlib import Path

# Input files
small_file = Path("/Users/crboatwright/PerryLetters/BFPerry_Letters_NER/BFPPeopleOnlySmallModel.txt")
medium_file = Path("/Users/crboatwright/PerryLetters/BFPerry_Letters_NER/BFPPeopleOnlyMediumModel.txt")
large_file = Path("/Users/crboatwright/PerryLetters/BFPerry_Letters_NER/BFPPeopleOnlyLargeModel.txt")
output_csv = Path("/Users/crboatwright/PerryLetters/BFPerry_Letters_NER/model_comparison.csv")

# Read each file (skip header line)
def read_names(filepath):
    lines = filepath.read_text(encoding="utf-8").strip().split('\n')
    # Skip first line (header) and return set of names
    return set(line.strip() for line in lines[1:] if line.strip())

small_names = read_names(small_file)
medium_names = read_names(medium_file)
large_names = read_names(large_file)

# Get all unique names across all models
all_names = sorted(small_names | medium_names | large_names)

# Write comparison CSV
with output_csv.open('w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Small Model', 'Medium Model', 'Large Model'])
    
    for name in all_names:
        writer.writerow([
            name,
            'X' if name in small_names else '',
            'X' if name in medium_names else '',
            'X' if name in large_names else ''
        ])

print(f"Comparison saved to {output_csv}")
print(f"Total unique names: {len(all_names)}")
print(f"  Small model:  {len(small_names)}")
print(f"  Medium model: {len(medium_names)}")
print(f"  Large model:  {len(large_names)}")