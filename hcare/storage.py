import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "assessments.sqlite3"

def save_assessment(report, path=DB_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute("CREATE TABLE IF NOT EXISTS assessments (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, name TEXT NOT NULL, base REAL NOT NULL, adjusted REAL NOT NULL, eligible INTEGER NOT NULL, report_json TEXT NOT NULL)")
        result = report["result"]
        con.execute("INSERT INTO assessments (created_at, name, base, adjusted, eligible, report_json) VALUES (?,?,?,?,?,?)", (report["generated_at_utc"], report["assessment"], result["base_index"], result["evidence_adjusted_index"], int(result["eligible"]), json.dumps(report)))
        con.commit()

def list_assessments(path=DB_PATH):
    path = Path(path)
    if not path.exists():
        return []
    with sqlite3.connect(path) as con:
        return [dict(zip(["id","created_at","name","base","adjusted","eligible"], row)) for row in con.execute("SELECT id, created_at, name, base, adjusted, eligible FROM assessments ORDER BY id DESC")]
