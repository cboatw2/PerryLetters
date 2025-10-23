import sqlite3
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

db_file = "BFPerryLetters.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()

geolocator = Nominatim(user_agent="perry_letters_geocoder")

def get_lat_long(name, state, country):
    try:
        location = geolocator.geocode(f"{name}, {state}, {country}", timeout=10)
        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        pass
    return None, None

# Select locations with non-null state and country and null latitude/longitude
cur.execute("""
    SELECT location_id, name, state, country
    FROM location
    WHERE state IS NOT NULL AND country IS NOT NULL
      AND (latitude IS NULL OR longitude IS NULL)
""")

for row in cur.fetchall():
    location_id, name, state, country = row
    lat, lon = get_lat_long(name, state, country)
    if lat is not None and lon is not None:
        cur.execute("""
            UPDATE location
            SET latitude=?, longitude=?
            WHERE location_id=?
        """, (lat, lon, location_id))
        print(f"Updated {name}, {state}, {country}: {lat}, {lon}")

conn.commit()
conn.close()
print("Latitude and longitude update complete.")