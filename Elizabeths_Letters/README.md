# Elizabeths_Letters

This folder contains scripts and data for topic modeling and named entity recognition of the transcribed letters written by Elizabeth Frances McCall Perry.

## Contents

- `EFMPerryTranscribedLetters.txt`: The transcribed letters to be analyzed.
- `EFMPerry_Letters_split/`: Folder containing each letter as a separate `.txt` file.
- `EFMPerry_NER_entities.csv`: Named entities (people and locations) extracted from the letters.
- `BFPerryLetters_NER_final.csv`: Named entities from B.F. Perry's letters (for comparison).
- `elizabeth_letters_lda_topics.csv`, `elizabeth_letters_topics.csv`: Topic modeling results.
- `shared_persons.txt`, `shared_locations.txt`: Shared entities between Elizabeth and B.F. Perry letters.
- **Scripts:**
  - `EFMPerry_Letters_split.py`
  - `EFMPerry_Letters_NERForSplitLetters.py`
  - `Liz_and_Ben_NER_Results_comparison.py`
  - `topic_modeling_lda_only.py`
  - `topic_modeling_with_ner.py`
  - `topic_modeling.py`

---


## Setting Up a Virtual Environment (Recommended)

**It is recommended to use a Python virtual environment for this project:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate     # On Windows

pip install -r [requirements.txt](http://_vscodecontentref_/0)
python -m spacy download en_core_web_sm
```
**Install Requirements**
After installing the requirments listed in `requirements.txt`, ensure you have the spaCy English model:

```bash
python3 -m spacy download en_core_web_sm
```

## How to Use the Scripts

### 1. Split Letters into Individual Files

**Script:** `EFMPerry_Letters_split.py`

**Purpose:**  
Splits `EFMPerryTranscribedLetters.txt` into individual letter files in the `EFMPerry_Letters_split/` directory.

**How to run:**
```bash
python EFMPerry_Letters_split.py
```
This will create one `.txt` file per letter in the `EFMPerry_Letters_split/` folder.

---

### 2. Named Entity Recognition (NER) on Split Letters

**Script:** `EFMPerry_Letters_NERForSplitLetters.py`

**Purpose:**  
Runs spaCy NER on each letter in `EFMPerry_Letters_split/` and saves the results to `EFMPerry_NER_entities.csv`.

**How to run:**
```bash
python EFMPerry_Letters_NERForSplitLetters.py
```
Make sure you have the spaCy English model installed:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

---

### 3. Compare NER Results Between Elizabeth and B.F. Perry

**Script:** `Liz_and_Ben_NER_Results_comparison.py`

**Purpose:**  
Compares the named entities (people and locations) found in Elizabeth's (`EFMPerry_NER_entities.csv`) and B.F. Perry's (`BFPerryLetters_NER_final.csv`) letters.  
Outputs shared and unique entities to `shared_persons.txt` and `shared_locations.txt`.

**How to run:**
```bash
python Liz_and_Ben_NER_Results_comparison.py
```

---

### 4. Topic Modeling (LDA Only)

**Script:** `topic_modeling_lda_only.py`

**Purpose:**  
Runs LDA topic modeling on the letters in `EFMPerryTranscribedLetters.txt`, filtering out named entities using `EFMPerry_NER_entities.csv`.

**How to run:**
```bash
pip install pandas scikit-learn matplotlib
python topic_modeling_lda_only.py
```
Outputs include:
- `elizabeth_letters_topics.csv`: Topic assignment for each letter.
- `lda_topics_visualization.png`: Visualization of the topics.

---

## Notes

- All scripts assume you are running them from the `Elizabeths_Letters` directory.
- Make sure all required data files are present in this folder.
- Only LDA is used for topic modeling in this workflow.
- NER filtering is applied automatically if `EFMPerry_NER_entities.csv` is present.

---