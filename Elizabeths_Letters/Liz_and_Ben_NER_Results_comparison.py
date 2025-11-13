import pandas as pd
from collections import Counter

# Read both CSV files
efm_df = pd.read_csv('EFMPerry_NER_entities.csv')
bfp_df = pd.read_csv('BFPerryLetters_NER_final.csv')

# Clean the data - remove NaN values and strip whitespace
efm_df = efm_df.dropna()
bfp_df = bfp_df.dropna()

efm_df['entity_name'] = efm_df['entity_name'].str.strip()
efm_df['entity_type'] = efm_df['entity_type'].str.strip()
bfp_df['entity_name'] = bfp_df['entity_name'].str.strip()
bfp_df['entity_type'] = bfp_df['entity_type'].str.strip()

# Separate by entity type
efm_persons = set(efm_df[efm_df['entity_type'] == 'PERSON']['entity_name'].unique())
efm_locations = set(efm_df[efm_df['entity_type'] == 'LOCATION']['entity_name'].unique())

bfp_persons = set(bfp_df[bfp_df['entity_type'] == 'PERSON']['entity_name'].unique())
bfp_locations = set(bfp_df[bfp_df['entity_type'] == 'LOCATION']['entity_name'].unique())

# Find shared entities
shared_persons = efm_persons.intersection(bfp_persons)
shared_locations = efm_locations.intersection(bfp_locations)

# Calculate statistics
print("=" * 60)
print("NAMED ENTITY COMPARISON REPORT")
print("=" * 60)
print()

print("PERSONS:")
print(f"  EFM Perry unique persons: {len(efm_persons)}")
print(f"  BF Perry unique persons: {len(bfp_persons)}")
print(f"  Shared persons: {len(shared_persons)}")
print(f"  Percentage shared (of EFM): {len(shared_persons)/len(efm_persons)*100:.1f}%")
print(f"  Percentage shared (of BFP): {len(shared_persons)/len(bfp_persons)*100:.1f}%")
print()

print("LOCATIONS:")
print(f"  EFM Perry unique locations: {len(efm_locations)}")
print(f"  BF Perry unique locations: {len(bfp_locations)}")
print(f"  Shared locations: {len(shared_locations)}")
print(f"  Percentage shared (of EFM): {len(shared_locations)/len(efm_locations)*100:.1f}%")
print(f"  Percentage shared (of BFP): {len(shared_locations)/len(bfp_locations)*100:.1f}%")
print()

print("=" * 60)
print("SHARED PERSONS (alphabetically):")
print("=" * 60)
for person in sorted(shared_persons):
    print(f"  {person}")
print()

print("=" * 60)
print("SHARED LOCATIONS (alphabetically):")
print("=" * 60)
for location in sorted(shared_locations):
    print(f"  {location}")
print()

# Optional: Find entities unique to each collection
efm_only_persons = efm_persons - bfp_persons
bfp_only_persons = bfp_persons - efm_persons

efm_only_locations = efm_locations - bfp_locations
bfp_only_locations = bfp_locations - efm_locations

print("=" * 60)
print("SUMMARY OF UNIQUE ENTITIES:")
print("=" * 60)
print(f"Persons only in EFM Perry: {len(efm_only_persons)}")
print(f"Persons only in BF Perry: {len(bfp_only_persons)}")
print(f"Locations only in EFM Perry: {len(efm_only_locations)}")
print(f"Locations only in BF Perry: {len(bfp_only_locations)}")

# Optional: Save results to files
with open('shared_persons.txt', 'w') as f:
    for person in sorted(shared_persons):
        f.write(f"{person}\n")

with open('shared_locations.txt', 'w') as f:
    for location in sorted(shared_locations):
        f.write(f"{location}\n")

print("\nResults saved to 'shared_persons.txt' and 'shared_locations.txt'")