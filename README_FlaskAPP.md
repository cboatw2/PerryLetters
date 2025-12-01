# Perry Letters - Flask Web Application

A Flask-based web application for exploring and analyzing Benjamin Franklin Perry's correspondence. This application provides tools for viewing letters, mapping locations, tracking people mentioned over time, and adding scholarly notes.

## Features

- **Letter Browser**: View and search through Perry's letters
- **People Tracking**: See who is mentioned in the letters and track mentions over time
- **Worldview Mapping**: Interactive maps showing letter origins, destinations, and mentioned locations tovVisualize Perry's geographic worldview through his correspondence
- **Notes System**: Add and manage scholarly notes for individual letters
- **Search**: Full-text search across all letters
- **Database Management**: Edit people and location records
- **Visualizations**: Letter count over time and people mentions over time

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd PerryLetters
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install spaCy language models** (for NER features)
   ```bash
   python -m spacy download en_core_web_sm
   python -m spacy download en_core_web_md
   python -m spacy download en_core_web_lg
   ```

## Project Structure

```
PERRYLETTERS/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── BFPerryLetters.db              # SQLite database
├── letter_notes.json              # Scholarly notes
├── .quarto/                       # Quarto configuration
├── _quarto.yml                    # Quarto project file
├── .gitignore                     # Git ignore file
├── BFPerry_Letters_Database/      # Database-related files
├── BFPerry_Letters_NER/           # Named Entity Recognition project
├── BFPerryLettersSeparated/       # Individual letter text files
│   └── BFPerry_Letter*.txt
├── data/                          # Data files
├── Elizabeths_Letters/            # Elizabeth's correspondence
├── Other_Perry_Projects/          # Additional Perry-related projects
├── Tesseract_OCR_Projects/        # OCR processing projects
├── templates/                     # Jinja2 HTML templates
│   ├── base.html
│   ├── notes.html
│   ├── worldview_mapping.html
│   └── ...
├── static/                        # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
└── venv/                          # Python virtual environment
```

## Running the Application

1. **Activate your virtual environment**
   ```bash
   source venv/bin/activate
   ```

2. **Run the Flask app**
   ```bash
   python app.py
   ```
   
   The app will start in debug mode on:
   ```
   http://127.0.0.1:5000
   ```

## Database

The application uses SQLite (`BFPerryLetters.db`) with the following main tables:
- `letter` - Letter metadata (sender, recipient, date, locations, year)
- `people` - People mentioned in letters
- `location` - Geographic locations with coordinates
- `mentioned_people` - Letters where people are mentioned
- `mentioned_location` - Letters where locations are mentioned

## Available Routes
- `/` - Home page with letter list
- `/letter/<int:letter_id>` - View individual letter
- `/people` - List of all people mentioned
- `/locations` - List of all locations mentioned
- `/search` - Search letters by content, sender, recipient, location, or date
- `/notes` - Add/edit/view scholarly notes

### Visualizations
- `/worldview_mapping` - Advanced worldview mapping with filters
- `/letter_locations` - Letter location relationships
- `/mentioned_people_over_time` - Chart of people mentions over time
- `/visualization` - Letter count by year

### Data Management
- `/location/edit/<int:location_id>` - Edit location details
- `/location/delete/<int:location_id>` - Delete location
- `/person/edit/<int:person_id>` - Edit person details
- `/person/delete/<int:person_id>` - Delete person


### Viewing Letters
- Navigate to the home page to browse all letters
- Click on a letter number to view its full content and metadata
- Letter text files are stored in `BFPerryLettersSeparated/`

### Search
- Use the search page to find letters by:
  - Sender name
  - Recipient name
  - Locations
- Content keywords

### Adding Notes
1. Navigate to `/notes`
2. Select a letter from the dropdown
3. Click "Go"
4. Enter your note in the text area
5. Click "Save Note"
6. Notes are saved in `letter_notes.json`
7. To delete a note, clear the text and click "Save Note"

### Location Mapping

**Worldview Mapping (`/worldview_mapping`):**
- Color-coded markers by location type
- Historical context for each year from data/year_context.json
- Click markers for letter details and links

### People Over Time
- Visualize how frequently people are mentioned across different time periods
- Interactive chart showing mention patterns by year

### Letter Count Visualization
- Bar chart showing number of letters per year (1842-1882)
- Helps identify periods of high correspondence activity
- Search functionality for filtering letters by sender, recipient, location, or keywords


### `letter_notes.json`
Stores scholarly notes for individual letters:
```json
{
  "BFPerry_Letter1.txt": "Your note content here...",
  "BFPerry_Letter564.txt": "Another note..."
}
```

### Letter Text Files
Individual letter text files in `BFPerryLettersSeparated/`:
- Format: `BFPerry_Letter{number}.txt`
- Loaded dynamically when viewing a letter


### Debug Mode
The app runs in debug mode by default (see bottom of `app.py`):
```python
if __name__ == "__main__":
    app.run(debug=True)
```

### Database Connection
The app uses Flask's `g` object for database connections:
```python
db = get_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM letter")
results = cursor.fetchall()
```

### Working with Letter Files
Letter files follow the naming pattern `BFPerry_Letter{number}.txt`:
```python
letter_number = 564
file_path = os.path.join(
    os.path.dirname(__file__), 
    'BFPerryLettersSeparated', 
    f'BFPerry_Letter{letter_number}.txt'
)
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

### Port Already in Use
```bash
# Use a different port
python app.py  # Then manually change port in app.py
# Or use Flask CLI
export FLASK_APP=app.py
flask run --port 5001
```

### Database Path Issues
The database path is hardcoded in `app.py`:
```python
DATABASE = "/Users/crboatwright/PerryLetters/BFPerryLetters.db"
```
Make sure this path is correct for your system.

### Letter Files Not Found
Ensure letter text files are in `BFPerryLettersSeparated/` and follow the naming pattern `BFPerry_Letter{number}.txt`.

### Missing Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

```

## Related Projects

- **BFPerry_Letters_NER**: Named Entity Recognition project for extracting people and locations
- **BFPerry_Letters_Database**: Database setup and management
- **Elizabeths_Letters**: Related correspondence from Elizabeth
- **Tesseract_OCR_Projects**: OCR processing for digitizing letters
- **Other_Perry_Projects**: Additional Perry-related research projects
