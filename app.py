from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3
import os
import json
import re
from collections import Counter
from datetime import datetime

app = Flask(__name__)
DATABASE = "/Users/crboatwright/PerryLetters/BFPerryLetters.db"
LETTERS_DIR = '/Users/crboatwright/PerryLetters/data/BFPerryLettersSeparated/Split_Letter_Files'

# load year context once at startup
def load_year_context():
    p = os.path.join(os.path.dirname(__file__), "data", "year_context.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        app.logger.error("load_year_context error: %s", e)
        return {}

YEAR_CONTEXT = load_year_context()

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
    conn = sqlite3.connect('BFPerryLetters.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            l.*,
            s.name as sender_name,
            r.name as recipient_name,
            loc_from.name as sent_from_location,
            loc_to.name as sent_to_location
        FROM letter l
        LEFT JOIN people s ON l.sender_id = s.person_id
        LEFT JOIN people r ON l.recipient_id = r.person_id
        LEFT JOIN location loc_from ON l.sent_from_location_id = loc_from.location_id
        LEFT JOIN location loc_to ON l.sent_to_location_id = loc_to.location_id
        ORDER BY l.letter_number
    '''
    
    cursor.execute(query)
    letters = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('index.html', letters=letters, query=None)

@app.route("/letter/<int:letter_number>")
def letter(letter_number):
    cur = get_db().cursor()
    # Change from id to letter_number
    cur.execute("SELECT * FROM letter WHERE letter_number=?", (letter_number,))
    letter = cur.fetchone()
    
    if not letter:
        return "Letter not found", 404
    
    # Read the letter text file
    letter_dict = dict(letter)
    file_path = os.path.join(
        LETTERS_DIR,
        f'BFPerry_Letter{letter_number}.txt'
    )
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            letter_dict['text'] = f.read()
    except FileNotFoundError:
        letter_dict['text'] = f"Letter text file not found: BFPerry_Letter{letter_number}.txt"
    except Exception as e:
        letter_dict['text'] = f"Error reading file: {str(e)}"
    
    return render_template("letter.html", letter=letter_dict)

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
    if not query:
        return render_template("index.html", letters=[], query="")
    
    conn = sqlite3.connect('BFPerryLetters.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all letters with their metadata
    search_query = '''
        SELECT 
            l.*,
            s.name as sender_name,
            r.name as recipient_name,
            loc_from.name as sent_from_location,
            loc_to.name as sent_to_location
        FROM letter l
        LEFT JOIN people s ON l.sender_id = s.person_id
        LEFT JOIN people r ON l.recipient_id = r.person_id
        LEFT JOIN location loc_from ON l.sent_from_location_id = loc_from.location_id
        LEFT JOIN location loc_to ON l.sent_to_location_id = loc_to.location_id
        ORDER BY l.letter_number
    '''
    
    cursor.execute(search_query)
    all_letters = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Filter letters by searching in metadata and file content
    filtered_letters = []
    search_lower = query.lower()
    
    for letter in all_letters:
        matched = False
        
        # Check metadata fields
        if (letter.get('sender_name') and search_lower in letter['sender_name'].lower()) or \
           (letter.get('recipient_name') and search_lower in letter['recipient_name'].lower()) or \
           (letter.get('sent_from_location') and search_lower in letter['sent_from_location'].lower()) or \
           (letter.get('sent_to_location') and search_lower in letter['sent_to_location'].lower()) or \
           (letter.get('date') and search_lower in str(letter['date']).lower()):
            matched = True
        
        # Construct file path using letter_number
        letter_number = letter.get('letter_number')
        if letter_number:
            file_path = os.path.join(
                LETTERS_DIR,
                f'BFPerry_Letter{letter_number}.txt'
            )
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if search_lower in content.lower():
                        matched = True
                    letter['content'] = content
            except FileNotFoundError:
                letter['content'] = f"Letter text file not found: {file_path}"
            except Exception as e:
                letter['content'] = f"Error reading file: {str(e)}"
        else:
            letter['content'] = "No letter number available"
        
        if matched:
            filtered_letters.append(letter)
    
    return render_template("index.html", letters=filtered_letters, query=query)

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
    
    # Enhanced debugging
    cur.execute("SELECT location_id, name, latitude, longitude FROM location WHERE location_id = 79")
    loc_79 = cur.fetchone()
    print(f"Location 79: ID={loc_79['location_id']}, Name={loc_79['name']}, Lat={loc_79['latitude']}, Lon={loc_79['longitude']}")
    
    cur.execute("""
        SELECT COUNT(*) FROM letter 
        WHERE sent_from_location_id = 79
    """)
    print(f"Letters sent from location 79: {cur.fetchone()[0]}")
    
    # Check a specific letter with location 79
    cur.execute("""
        SELECT l.letter_number, l.sent_from_location_id,
               from_loc.name AS sent_from, from_loc.latitude AS from_lat, from_loc.longitude AS from_lon
        FROM letter l
        LEFT JOIN location AS from_loc ON l.sent_from_location_id = from_loc.location_id
        WHERE l.sent_from_location_id = 79
        LIMIT 1
    """)
    sample = cur.fetchone()
    if sample:
        print(f"Sample letter {sample['letter_number']}: from={sample['sent_from']}, lat={sample['from_lat']}, lon={sample['from_lon']}")
    
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

        letter_dict = {
            "letter_id": letter["id"],
            "letter_number": letter["letter_number"],
            "date": letter["date"],
            "year": year,
            "sent_from": {"name": letter["sent_from"], "lat": letter["from_lat"], "lon": letter["from_lon"]},
            "sent_to": {"name": letter["sent_to"], "lat": letter["to_lat"], "lon": letter["to_lon"]},
            "mentioned": mentioned
        }
        
        # Debug: Print if this letter is from Washington D.C.
        if letter["sent_from"] == "Washington D.C.":
            print(f"Letter {letter['letter_number']}: sent_from = {letter_dict['sent_from']}")
        
        letter_data.append(letter_dict)

    year_context = load_year_context()
    years = ["All"] + sorted(years, key=int)

    return render_template(
        "worldview_mapping.html",
        letter_data=letter_data,
        years=years,
        year_context=year_context
    )

# Load and parse the letters data
def load_letters():
    with open('BFPerryLetters_split.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    letters = []
    letter_blocks = content.split('---')
    
    for block in letter_blocks:
        if block.strip():
            letter = {}
            lines = block.strip().split('\n')
            for line in lines:
                if line.startswith('Date:'):
                    letter['date'] = line.replace('Date:', '').strip()
                elif line.startswith('From:'):
                    letter['from'] = line.replace('From:', '').strip()
                elif line.startswith('To:'):
                    letter['to'] = line.replace('To:', '').strip()
                elif line.startswith('Location:'):
                    letter['location'] = line.replace('Location:', '').strip()
                elif line.startswith('Content:'):
                    letter['content'] = line.replace('Content:', '').strip()
            if letter:
                letters.append(letter)
    
    return letters

@app.route('/letters_split')
def letters_split():
    letters = load_letters()
    return render_template('letters_split.html', letters=letters)

@app.route('/search_split')
def search_split():
    query = request.args.get('q', '')
    letters = load_letters()
    
    if query:
        filtered_letters = []
        for letter in letters:
            if (query.lower() in letter.get('content', '').lower() or
                query.lower() in letter.get('from', '').lower() or
                query.lower() in letter.get('to', '').lower() or
                query.lower() in letter.get('location', '').lower()):
                filtered_letters.append(letter)
        letters = filtered_letters
    
    return render_template('search_split.html', letters=letters, query=query)

@app.route('/visualization_split')
def visualization_split():
    letters = load_letters()
    
    # Extract years from dates and count them
    year_counts = Counter()
    
    for letter in letters:
        date_str = letter.get('date', '')
        # Try to extract year from various date formats
        year_match = re.search(r'\b(18\d{2}|19\d{2}|20\d{2})\b', date_str)
        if year_match:
            year = int(year_match.group(1))
            year_counts[year] += 1
    
    # Sort by year
    sorted_years = sorted(year_counts.items())
    years = [str(year) for year, count in sorted_years]
    counts = [count for year, count in sorted_years]
    
    return render_template('visualization_split.html', years=years, counts=counts)

@app.route('/visualization')
def visualization():
    cur = get_db().cursor()
    
    # Get all letters with their years
    cur.execute("""
        SELECT year FROM letter 
        WHERE year IS NOT NULL AND year != ''
        ORDER BY year
    """)
    letters = cur.fetchall()
    
    # Count letters by year
    from collections import Counter
    year_counts = Counter()
    for letter in letters:
        year = letter['year'].strip()
        if year.isdigit() and 1842 <= int(year) <= 1882:
            year_counts[int(year)] += 1
    
    # Sort by year
    sorted_years = sorted(year_counts.items())
    years = [str(year) for year, count in sorted_years]
    counts = [count for year, count in sorted_years]
    
    return render_template('lettercount.html', years=years, counts=counts)

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    notes_file = '/Users/crboatwright/PerryLetters/data/letter_notes.json'  # ✅ Full path to data folder
    letters_dir = LETTERS_DIR

    # Get all letter files
    letter_files = sorted(
        [f for f in os.listdir(letters_dir) if f.endswith('.txt')],
        key=lambda x: int(''.join(filter(str.isdigit, x)))
    )
    letter_numbers = [f.replace('BFPerry_Letter', '').replace('.txt', '') for f in letter_files]

    # Load existing notes
    if os.path.exists(notes_file):
        with open(notes_file, 'r', encoding='utf-8') as f:
            notes_data = json.load(f)
    else:
        notes_data = {}

    current_letter = request.args.get('letter')
    if request.method == 'POST':
        current_letter = request.form.get('current_letter')
        note_val = request.form.get('note', '')
        letter_key = f'BFPerry_Letter{current_letter}.txt'

        if note_val.strip():
            notes_data[letter_key] = note_val
        elif letter_key in notes_data:
            del notes_data[letter_key]

        with open(notes_file, 'w', encoding='utf-8') as f:
            json.dump(notes_data, f, indent=2)

        return redirect(url_for('notes', letter=current_letter))

    return render_template(
        'notes.html',
        letter_files=letter_files,
        letter_numbers=letter_numbers,
        notes_data=notes_data,
        current_letter=current_letter
    )

@app.route("/lettercount")
def lettercount():
    import os
    query = request.args.get("query", "").strip()
    
    cur = get_db().cursor()
    
    if query:
        # Search mode: count mentions of the query term by year
        cur.execute("""
            SELECT year, COUNT(*) as count 
            FROM letter 
            WHERE year IS NOT NULL AND year != ''
            GROUP BY year 
            ORDER BY year
        """)
        year_data = cur.fetchall()
        
        # Count mentions in each year
        year_counts = {}
        search_lower = query.lower()
        
        for row in year_data:
            year = str(row['year'])
            year_counts[year] = 0
        
        # Get all letters with years
        cur.execute("""
            SELECT letter_number, year 
            FROM letter 
            WHERE year IS NOT NULL AND year != ''
        """)
        all_letters = cur.fetchall()
        
        # Search through letter files
        for letter in all_letters:
            letter_number = letter['letter_number']
            year = str(letter['year'])
            
            file_path = os.path.join(
                LETTERS_DIR,
                f'BFPerry_Letter{letter_number}.txt'
            )
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    # Count occurrences of search term
                    mention_count = content.count(search_lower)
                    if mention_count > 0:
                        year_counts[year] = year_counts.get(year, 0) + mention_count
            except FileNotFoundError:
                continue
            except Exception:
                continue
        
        years = sorted(year_counts.keys())
        counts = [year_counts[y] for y in years]
        
    else:
        # Default mode: show letter counts by year
        cur.execute("""
            SELECT year, COUNT(*) as count 
            FROM letter 
            WHERE year IS NOT NULL AND year != ''
            GROUP BY year 
            ORDER BY year
        """)
        data = cur.fetchall()
        years = [str(row['year']) for row in data]
        counts = [row['count'] for row in data]
    
    return render_template("lettercount.html", years=years, counts=counts, query=query)

if __name__ == "__main__":
    app.run(debug=True)