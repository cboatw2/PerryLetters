import csv

input_file = "NER_long_table.csv"
output_file = "NER_long_table_deduped.csv"

unique_rows = set()
deduped_rows = []

with open(input_file, "r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)
    deduped_rows.append(header)
    for row in reader:
        row_tuple = tuple(row)
        if row_tuple not in unique_rows:
            unique_rows.add(row_tuple)
            deduped_rows.append(row)

with open(output_file, "w", encoding="utf-8", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerows(deduped_rows)

print(f"Deduplicated table saved as {output_file}")