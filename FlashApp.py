from flask import Flask, render_template, g
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
    cur.execute("SELECT * FROM people ORDER BY name")
    people = cur.fetchall()
    return render_template("people.html", people=people)

@app.route("/locations")
def locations():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM location ORDER BY name")
    locations = cur.fetchall()
    return render_template("locations.html", locations=locations)

if __name__ == "__main__":
    app.run(debug=True)