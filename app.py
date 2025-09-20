from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "BFPerryLetters.db"

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
    cur.execute("SELECT * FROM location ORDER BY name")
    locations = cur.fetchall()
    return render_template("locations.html", locations=locations)

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
        cur.execute("UPDATE location SET name=? WHERE location_id=?", (name, location_id))
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

if __name__ == "__main__":
    app.run(debug=True)