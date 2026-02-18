from src.ingest import ingest_transactions
from src.analysis import run_analysis
from src.advice import generate_advice
from src.persist import add_rows
from src.db import init_db, reset_db, db_stats, category_summary_sql

import argparse


def main():
    parser = argparse.ArgumentParser(description="Personal Finance Assistant (Phase 4.5)")
    parser.add_argument("--input", default="data/raw_transactions.csv", help="Path to raw CSV input")
    parser.add_argument("--clean", default="data/clean_transactions.csv", help="Path to clean CSV output")
    parser.add_argument("--db", default="data/finance.db", help="Path to SQLite database")
    parser.add_argument("--reset-db", action="store_true", help="Drop + recreate database before run")
    parser.add_argument("--no-persist", action="store_true", help="Skip ingest + persist (analyze existing DB only)")

    args = parser.parse_args()

    #Ensure DB exists (and optionally reset it)
    init_db()
    if args.reset_db:
        reset_db()
        print("✅ Database reset.")
        print("-" * 30)

    ingest_summary = None
    persist_summary = None

    #Ingest + clean + persist (unless skipped)
    if not args.no_persist:
        ingest_summary = ingest_transactions(
            input_path=args.input,
            output_path=args.clean,
        )

        clean_path = ingest_summary["output_path"]
        persist_summary = add_rows(clean_path)

        #Ingest report
        print("Ingest Report")
        print("-" * 30)
        print(f"- Input:        {args.input}")
        print(f"- Output:       {clean_path}")
        print(f"- Rows read:    {ingest_summary['rows_read']}")
        print(f"- Rows written: {ingest_summary['rows_written']}")
        print(f"- Rows skipped: {ingest_summary['rows_skipped']}")
        print(f"- Skip reasons: {ingest_summary['skip_reasons']}")
        print("-" * 30)

        print("Database Persist Report")
        print(persist_summary)
        print("-" * 30)

        #Early exit if no valid data
        if ingest_summary["rows_written"] == 0:
            print("No valid transactions found. Analysis aborted.")
            return

        #Optional warning for suspicious files
        if ingest_summary["rows_read"] > 0 and ingest_summary["rows_written"] < 0.5 * ingest_summary["rows_read"]:
            print("⚠️ Warning: More than half of the rows were skipped.")
            print("-" * 30)

    #DB stats (always useful, even with --no-persist)
    stats = db_stats()
    print("DB Stats")
    print("-" * 30)
    print(f"- Rows in DB: {stats['rows_in_db']}")
    print(f"- Date range: {stats['min_date']} → {stats['max_date']}")
    print("-" * 30)

    if stats["rows_in_db"] == 0:
        print("Database is empty. Nothing to analyze.")
        return

    results = run_analysis(args.db)
    print(results)


    advice = generate_advice(results)
    print("Spending Summary")
    print("-" * 30)
    for line in advice:
        print("-", line)
    print("-" * 30)

    print("Top Categories (SQL)")
    print("-" * 30)
    for row in category_summary_sql(limit=10):
        print(f"- {row['category']}: {row['total']:.2f} ({row['n']} txns)")


if __name__ == "__main__":
    main()