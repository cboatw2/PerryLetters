from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3
import json

app = Flask(__name__)
DATABASE = "BFPerryLetters.db"

# load year context once at startup
try:
    with open("year_context.json", "r", encoding="utf-8") as f:
        YEAR_CONTEXT = json.load(f)
except Exception:
    YEAR_CONTEXT = {}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM letter ORDER BY letter_number")
    letters = cur.fetchall()
    return render_template("index.html", letters=letters)

@app.route("/letter/<int:letter_id>")
def letter(letter_id):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM letter WHERE id=?", (letter_id,))
    letter = cur.fetchone()
    return render_template("letter.html", letter=letter)

@app.route("/people")
def people():
    cur = get_db().cursor()
    # Get all people
    cur.execute("SELECT * FROM people")
    people = cur.fetchall()

    # For each person, get the letter numbers where they are mentioned
    person_letters = {}
    for person in people:
        cur.execute("""
            SELECT letter.letter_number, letter.file_path
            FROM mentioned_people
            JOIN letter ON mentioned_people.letter_id = letter.id
            WHERE mentioned_people.person_id = ?
        """, (person['person_id'],))
        person_letters[person['person_id']] = cur.fetchall()

    return render_template("people.html", people=people, person_letters=person_letters)

@app.route("/locations")
def locations():
    cur = get_db().cursor()
    # Only select locations that are mentioned in at least one letter
    cur.execute("""
        SELECT * FROM location
        WHERE location_id IN (
            SELECT DISTINCT location_id FROM mentioned_location
        )
        ORDER BY name
    """)
    locations = cur.fetchall()

    # For each location, get the letter numbers where it is mentioned
    location_letters = {}
    for loc in locations:
        cur.execute("""
            SELECT letter.letter_number, letter.file_path
            FROM mentioned_location
            JOIN letter ON mentioned_location.letter_id = letter.id
            WHERE mentioned_location.location_id = ?
        """, (loc['location_id'],))
        location_letters[loc['location_id']] = cur.fetchall()

    return render_template("locations.html", locations=locations, location_letters=location_letters)

@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    cur = get_db().cursor()
    # Search by person name or location name
    cur.execute("""
        SELECT letter.*
        FROM letter
        LEFT JOIN people AS sender ON letter.sender_id = sender.person_id
        LEFT JOIN people AS recipient ON letter.recipient_id = recipient.person_id
        LEFT JOIN location AS from_loc ON letter.sent_from_location_id = from_loc.location_id
        LEFT JOIN location AS to_loc ON letter.sent_to_location_id = to_loc.location_id
        WHERE sender.name LIKE ? OR recipient.name LIKE ? OR from_loc.name LIKE ? OR to_loc.name LIKE ?
        ORDER BY letter.letter_number
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
    letters = cur.fetchall()
    return render_template("index.html", letters=letters, query=query)

@app.route("/mentioned_people_over_time")
def mentioned_people_over_time():
    cur = get_db().cursor()
    cur.execute("""
        SELECT 
            SUBSTR(letter.date, -4, 4) AS year,
            COUNT(DISTINCT mentioned_people.person_id) AS count
        FROM mentioned_people
        JOIN letter ON mentioned_people.letter_id = letter.id
        WHERE LENGTH(letter.date) >= 4
        GROUP BY year
        ORDER BY year
    """)
    data = cur.fetchall()
    years = [row['year'] for row in data]
    counts = [row['count'] for row in data]
    return render_template("mentioned_people_over_time.html", years=years, counts=counts)

@app.route("/location/edit/<int:location_id>", methods=["GET", "POST"])
def edit_location(location_id):
    cur = get_db().cursor()
    if request.method == "POST":
        name = request.form["name"]
        state = request.form.get("state", "")
        country = request.form.get("country", "")
        cur.execute(
            "UPDATE location SET name=?, state=?, country=? WHERE location_id=?",
            (name, state, country, location_id)
        )
        get_db().commit()
        return redirect(url_for('locations'))
    cur.execute("SELECT * FROM location WHERE location_id=?", (location_id,))
    location = cur.fetchone()
    return render_template("edit_location.html", location=location)

@app.route("/location/delete/<int:location_id>", methods=["POST"])
def delete_location(location_id):
    cur = get_db().cursor()
    cur.execute("DELETE FROM location WHERE location_id=?", (location_id,))
    get_db().commit()
    return redirect(url_for('locations'))

@app.route("/person/edit/<int:person_id>", methods=["GET", "POST"])
def edit_person(person_id):
    cur = get_db().cursor()
    if request.method == "POST":
        name = request.form["name"]
        cur.execute("UPDATE people SET name=? WHERE person_id=?", (name, person_id))
        get_db().commit()
        return redirect(url_for('people'))
    cur.execute("SELECT * FROM people WHERE person_id=?", (person_id,))
    person = cur.fetchone()
    return render_template("edit_person.html", person=person)

@app.route("/person/delete/<int:person_id>", methods=["POST"])
def delete_person(person_id):
    cur = get_db().cursor()
    cur.execute("DELETE FROM people WHERE person_id=?", (person_id,))
    get_db().commit()
    return redirect(url_for('people'))

@app.route("/letter_locations")
def letter_locations():
    cur = get_db().cursor()
    # Only include letters where sender_id is in the allowed list
    allowed_senders = (1, 143, 261, 267, 447, 935)
    cur.execute(f"""
        SELECT l.id, l.letter_number, l.date,
               from_loc.name AS sent_from,
               to_loc.name AS sent_to
        FROM letter l
        LEFT JOIN location AS from_loc ON l.sent_from_location_id = from_loc.location_id
        LEFT JOIN location AS to_loc ON l.sent_to_location_id = to_loc.location_id
        WHERE l.sender_id IN {allowed_senders}
        ORDER BY l.letter_number
    """)
    letters = cur.fetchall()

    # For each letter, get mentioned locations
    letter_mentions = {}
    for letter in letters:
        cur.execute("""
            SELECT loc.name
            FROM mentioned_location
            JOIN location AS loc ON mentioned_location.location_id = loc.location_id
            WHERE mentioned_location.letter_id = ?
        """, (letter['id'],))
        letter_mentions[letter['id']] = [row['name'] for row in cur.fetchall()]

    return render_template("letter_locations.html", letters=letters, letter_mentions=letter_mentions)

@app.route("/map")
def map_view():
    cur = get_db().cursor()
    cur.execute("""
        SELECT l.id, l.letter_number, l.date, l.year,
               from_loc.name AS sent_from, from_loc.latitude AS from_lat, from_loc.longitude AS from_lon,
               to_loc.name AS sent_to, to_loc.latitude AS to_lat, to_loc.longitude AS to_lon
        FROM letter l
        LEFT JOIN location AS from_loc ON l.sent_from_location_id = from_loc.location_id
        LEFT JOIN location AS to_loc ON l.sent_to_location_id = to_loc.location_id
        ORDER BY l.letter_number
    """)
    letters = cur.fetchall()

    letter_data = []
    years = set()
    for letter in letters:
        # prefer the year column, fall back to last 4 chars of date
        year = (letter["year"] or "").strip()
        if not year and letter["date"]:
            year = letter["date"][-4:]
        # only keep valid numeric years in range
        if year.isdigit() and 1842 <= int(year) <= 1882:
            years.add(year)

        cur.execute("""
            SELECT loc.name, loc.latitude, loc.longitude
            FROM mentioned_location
            JOIN location AS loc ON mentioned_location.location_id = loc.location_id
            WHERE mentioned_location.letter_id = ?
        """, (letter['id'],))
        mentioned = [dict(name=row[0], lat=row[1], lon=row[2]) for row in cur.fetchall()]

        letter_data.append({
            "letter_id": letter["id"],
            "letter_number": letter["letter_number"],
            "date": letter["date"],
            "year": year,
            "sent_from": {"name": letter["sent_from"], "lat": letter["from_lat"], "lon": letter["from_lon"]},
            "sent_to": {"name": letter["sent_to"], "lat": letter["to_lat"], "lon": letter["to_lon"]},
            "mentioned": mentioned
        })

    return render_template(
        "map.html",
        letter_data=letter_data,
        years=sorted(years, key=int),
        year_context=YEAR_CONTEXT
    )

@app.route("/worldview_mapping")
def worldview_mapping():
    cur = get_db().cursor()
    cur.execute("""
        SELECT l.id, l.letter_number, l.date, l.year,
               from_loc.name AS sent_from, from_loc.latitude AS from_lat, from_loc.longitude AS from_lon,
               to_loc.name AS sent_to, to_loc.latitude AS to_lat, to_loc.longitude AS to_lon
        FROM letter l
        LEFT JOIN location AS from_loc ON l.sent_from_location_id = from_loc.location_id
        LEFT JOIN location AS to_loc ON l.sent_to_location_id = to_loc.location_id
        ORDER BY l.letter_number
    """)
    letters = cur.fetchall()

    letter_data = []
    years = set()
    for letter in letters:
        cur.execute("""
            SELECT loc.name, loc.latitude, loc.longitude
            FROM mentioned_location
            JOIN location AS loc ON mentioned_location.location_id = loc.location_id
            WHERE mentioned_location.letter_id = ?
        """, (letter['id'],))
        mentioned = [dict(name=row[0], lat=row[1], lon=row[2]) for row in cur.fetchall()]

        year = (letter["year"] or "").strip()
        if not year and letter["date"]:
            year = letter["date"][-4:]
        if year.isdigit() and 1842 <= int(year) <= 1882:
            years.add(year)

        letter_data.append({
            "letter_id": letter["id"],
            "letter_number": letter["letter_number"],
            "date": letter["date"],
            "year": year,
            "sent_from": {"name": letter["sent_from"], "lat": letter["from_lat"], "lon": letter["from_lon"]},
            "sent_to": {"name": letter["sent_to"], "lat": letter["to_lat"], "lon": letter["to_lon"]},
            "mentioned": mentioned
        })

    years = ["All"] + sorted(years, key=int)

    return render_template(
        "worldview_mapping.html",
        letter_data=letter_data,
        years=years,
        year_context=YEAR_CONTEXT
    )

# year_context variable as suggested
year_context = {
  "1861": {
    "Personal": ["Letter about family farm"],
    "South Carolina": ["SC militia mobilizes"],
    "National": ["Civil War begins"],
    "International": ["European reaction"]
  },
  # ... other years ...
}

if __name__ == "__main__":
    app.run(debug=True)