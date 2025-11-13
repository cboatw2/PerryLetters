import pandas as pd
from collections import Counter
import os

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Read both CSV files with error handling
print("Loading EFM Perry entities...")
efm_df = pd.read_csv(os.path.join(script_dir, 'EFMPerry_NER_entities.csv'))

print("Loading BF Perry entities...")
# Use the path to the BFPerry_Letters_NER directory
bfp_path = os.path.join(script_dir, '..', 'BFPerry_Letters_NER', 'BFPerryLetters_NER_final.csv')

# Read with error handling for malformed lines
try:
    bfp_df = pd.read_csv(bfp_path, on_bad_lines='skip', engine='python')
except:
    # If that doesn't work, try with different error handling
    bfp_df = pd.read_csv(bfp_path, error_bad_lines=False, warn_bad_lines=True)

print(f"Loaded {len(efm_df)} EFM entities and {len(bfp_df)} BF Perry entities")

# Clean the data - remove NaN values and strip whitespace
efm_df = efm_df.dropna(subset=['entity_name', 'entity_type'])
bfp_df = bfp_df.dropna(subset=['entity_name', 'entity_type'])

# Remove empty strings
efm_df = efm_df[efm_df['entity_name'].str.strip() != '']
bfp_df = bfp_df[bfp_df['entity_name'].str.strip() != '']

efm_df['entity_name'] = efm_df['entity_name'].str.strip()
efm_df['entity_type'] = efm_df['entity_type'].str.strip()
bfp_df['entity_name'] = bfp_df['entity_name'].str.strip()
bfp_df['entity_type'] = bfp_df['entity_type'].str.strip()

print(f"After cleaning: {len(efm_df)} EFM entities and {len(bfp_df)} BF Perry entities")

# Separate by entity type
efm_persons = set(efm_df[efm_df['entity_type'] == 'PERSON']['entity_name'].unique())
efm_locations = set(efm_df[efm_df['entity_type'] == 'LOCATION']['entity_name'].unique())

bfp_persons = set(bfp_df[bfp_df['entity_type'] == 'PERSON']['entity_name'].unique())
bfp_locations = set(bfp_df[bfp_df['entity_type'] == 'LOCATION']['entity_name'].unique())

# Find shared entities
shared_persons = efm_persons.intersection(bfp_persons)
shared_locations = efm_locations.intersection(bfp_locations)

# Calculate statistics
print("\n" + "=" * 60)
print("NAMED ENTITY COMPARISON REPORT")
print("=" * 60)
print()

print("PERSONS:")
print(f"  EFM Perry unique persons: {len(efm_persons)}")
print(f"  BF Perry unique persons: {len(bfp_persons)}")
print(f"  Shared persons: {len(shared_persons)}")
if len(efm_persons) > 0:
    print(f"  Percentage shared (of EFM): {len(shared_persons)/len(efm_persons)*100:.1f}%")
if len(bfp_persons) > 0:
    print(f"  Percentage shared (of BFP): {len(shared_persons)/len(bfp_persons)*100:.1f}%")
print()

print("LOCATIONS:")
print(f"  EFM Perry unique locations: {len(efm_locations)}")
print(f"  BF Perry unique locations: {len(bfp_locations)}")
print(f"  Shared locations: {len(shared_locations)}")
if len(efm_locations) > 0:
    print(f"  Percentage shared (of EFM): {len(shared_locations)/len(efm_locations)*100:.1f}%")
if len(bfp_locations) > 0:
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

# Find entities unique to each collection
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
print()

# Show some examples of unique entities
if efm_only_persons:
    print("Examples of persons only in EFM Perry (first 10):")
    for person in sorted(efm_only_persons)[:10]:
        print(f"  {person}")
    print()

if bfp_only_persons:
    print("Examples of persons only in BF Perry (first 10):")
    for person in sorted(bfp_only_persons)[:10]:
        print(f"  {person}")
    print()

# Save results to files
output_dir = script_dir
shared_persons_path = os.path.join(output_dir, 'shared_persons.txt')
shared_locations_path = os.path.join(output_dir, 'shared_locations.txt')

with open(shared_persons_path, 'w') as f:
    for person in sorted(shared_persons):
        f.write(f"{person}\n")

with open(shared_locations_path, 'w') as f:
    for location in sorted(shared_locations):
        f.write(f"{location}\n")

print(f"\nResults saved to:")
print(f"  - {shared_persons_path}")
print(f"  - {shared_locations_path}")