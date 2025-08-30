import spacy

nlp = spacy.load("en_core_web_sm")

input_file = "BFPerry_Letters_1863-1882.txt"

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

doc = nlp(text)

persons = set()
places = set()
for ent in doc.ents:
    if ent.label_ == "PERSON":
        persons.add(ent.text)
    elif ent.label_ == "GPE":
        places.add(ent.text)

with open("NER_results.txt", "a", encoding="utf-8") as out:
    out.write(f"\n=== Results from {input_file} ===\n")
    out.write("Persons:\n")
    for name in sorted(persons):
        out.write(name + "\n")
    out.write("\nPlaces:\n")
    for place in sorted(places):
        out.write(place + "\n")