#!/usr/bin/env python3
import argparse
import csv
import os
import re
import sqlite3
from collections import defaultdict

UNIONISM_PEOPLE_COLUMNS = [
    "canonical_key",  # helper key for staging/join
    "full_name",
    "display_name",
    "birth_year",
    "death_year",
    "birth_place_id",
    "death_place_id",
    "race_code",
    "gender",
    "class_code",
    "occupation",
    "home_region_sc_code",
    "enslaved_status",
    "source_density_code",
    "representation_depth_code",
    "erasure_flag",
    "erasure_reason_code",
    "notes",
]

ALIASES_STAGING_COLUMNS = [
    "canonical_key",  # helper key; resolved to person_id during load
    "alias_name",
    "source_id",
    "notes",
]

REVIEW_COLUMNS = [
    "raw_person_id",
    "raw_name",
    "normalized_name",
    "canonical_key",
    "suggested_canonical_name",
    "mention_letters_count",
    "sender_letters_count",
    "recipient_letters_count",
    "action",                # keep, merge, drop, review
    "canonical_name_override",
    "notes",
]


def normalize_name(name: str) -> str:
    n = (name or "").strip()
    n = n.lower()
    n = n.replace("’", "'")
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"[^\w\s']", "", n)  # drop punctuation except apostrophe
    n = n.strip()
    return n


def canonical_key_from_name(name: str) -> str:
    n = normalize_name(name)
    n = n.replace(" ", "_")
    return n or "unknown"


def choose_suggested_canonical(names):
    # Simple heuristic: longest non-empty variant usually has most context.
    cleaned = [n.strip() for n in names if (n or "").strip()]
    if not cleaned:
        return ""
    cleaned.sort(key=lambda x: (len(x), x.lower()), reverse=True)
    return cleaned[0]


def fetch_people_with_context(conn):
    sql = """
    SELECT
        p.person_id,
        p.name AS raw_name,
        COALESCE(mp.mention_letters_count, 0) AS mention_letters_count,
        COALESCE(s.sender_letters_count, 0) AS sender_letters_count,
        COALESCE(r.recipient_letters_count, 0) AS recipient_letters_count
    FROM people p
    LEFT JOIN (
        SELECT person_id, COUNT(DISTINCT letter_id) AS mention_letters_count
        FROM mentioned_people
        GROUP BY person_id
    ) mp ON mp.person_id = p.person_id
    LEFT JOIN (
        SELECT sender_id AS person_id, COUNT(*) AS sender_letters_count
        FROM letter
        WHERE sender_id IS NOT NULL
        GROUP BY sender_id
    ) s ON s.person_id = p.person_id
    LEFT JOIN (
        SELECT recipient_id AS person_id, COUNT(*) AS recipient_letters_count
        FROM letter
        WHERE recipient_id IS NOT NULL
        GROUP BY recipient_id
    ) r ON r.person_id = p.person_id
    ORDER BY p.name COLLATE NOCASE, p.person_id;
    """
    cur = conn.execute(sql)
    return [dict(row) for row in cur.fetchall()]


def write_csv(path, columns, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in columns})


def build_staging(source_db, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    conn = sqlite3.connect(source_db)
    conn.row_factory = sqlite3.Row
    try:
        raw_rows = fetch_people_with_context(conn)
    finally:
        conn.close()

    # Group raw names by normalized canonical key.
    groups = defaultdict(list)
    for r in raw_rows:
        raw_name = (r.get("raw_name") or "").strip()
        key = canonical_key_from_name(raw_name)
        r["normalized_name"] = normalize_name(raw_name)
        r["canonical_key"] = key
        groups[key].append(r)

    # Suggested canonical name per group.
    suggested_name_by_key = {}
    for key, rows in groups.items():
        suggested_name_by_key[key] = choose_suggested_canonical([x["raw_name"] for x in rows])

    # 1) Review file (you edit this file)
    review_rows = []
    for r in raw_rows:
        key = r["canonical_key"]
        review_rows.append({
            "raw_person_id": r["person_id"],
            "raw_name": r["raw_name"],
            "normalized_name": r["normalized_name"],
            "canonical_key": key,
            "suggested_canonical_name": suggested_name_by_key[key],
            "mention_letters_count": r["mention_letters_count"],
            "sender_letters_count": r["sender_letters_count"],
            "recipient_letters_count": r["recipient_letters_count"],
            "action": "review",
            "canonical_name_override": "",
            "notes": "",
        })

    # 2) Unionism people staging (one row per canonical key)
    people_rows = []
    for key, rows in groups.items():
        suggested = suggested_name_by_key[key]
        source_ids = sorted(str(x["person_id"]) for x in rows)
        notes = f"Imported from BFPerry people ids: {','.join(source_ids)}"
        people_rows.append({
            "canonical_key": key,
            "full_name": suggested,
            "display_name": suggested,
            "birth_year": "",
            "death_year": "",
            "birth_place_id": "",
            "death_place_id": "",
            "race_code": "",
            "gender": "",
            "class_code": "",
            "occupation": "",
            "home_region_sc_code": "",
            "enslaved_status": "",
            "source_density_code": "",
            "representation_depth_code": "",
            "erasure_flag": 0,
            "erasure_reason_code": "",
            "notes": notes,
        })

    # 3) Alias staging (every raw variant)
    alias_rows = []
    seen_alias = set()
    for key, rows in groups.items():
        for r in rows:
            alias = (r["raw_name"] or "").strip()
            if not alias:
                continue
            dedupe_key = (key, alias.lower())
            if dedupe_key in seen_alias:
                continue
            seen_alias.add(dedupe_key)
            alias_rows.append({
                "canonical_key": key,
                "alias_name": alias,
                "source_id": "",
                "notes": f"From BFPerry person_id={r['person_id']}",
            })

    review_path = os.path.join(out_dir, "people_review.csv")
    people_path = os.path.join(out_dir, "unionism_people_staging.csv")
    alias_path = os.path.join(out_dir, "unionism_aliases_staging.csv")

    write_csv(review_path, REVIEW_COLUMNS, review_rows)
    write_csv(people_path, UNIONISM_PEOPLE_COLUMNS, people_rows)
    write_csv(alias_path, ALIASES_STAGING_COLUMNS, alias_rows)

    print("Wrote:")
    print(f"  {review_path}")
    print(f"  {people_path}")
    print(f"  {alias_path}")


def main():
    parser = argparse.ArgumentParser(description="Build staging CSVs from BFPerryLetters.db for UnionismNetwork.")
    parser.add_argument("--source-db", required=True, help="Path to BFPerryLetters.db")
    parser.add_argument("--out-dir", required=True, help="Output folder for staging CSVs")
    args = parser.parse_args()
    build_staging(args.source_db, args.out_dir)


if __name__ == "__main__":
    main()