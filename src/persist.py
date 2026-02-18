from src.db import connect, init_db, insert_transactions
from src.ingest import ingest_transactions
import csv
input_path = 'data/clean_transactions.csv'
def load_clean_csv(clean_path = input_path):
    with open(clean_path, "r", newline="", encoding="utf-8") as clean_t:
        rows: list[dict] = []
        reader = csv.DictReader(clean_t)
        for r in reader:
            r["amount"] = float(r["amount"])
            r["abs_amount"] = float(r["abs_amount"])
            r["merchant"] = r["merchant"].strip().lower()
            r["category"] = r["category"].strip()
            rows.append(r)
    return rows
def add_rows(clean_path = input_path):
    init_db()
    rows = load_clean_csv(clean_path)
    inserted = insert_transactions(rows)

    return {
        "clean_csv_path": clean_path,
        "rows_loaded": len(rows),
        "rows_inserted": inserted,
    }

     




    




