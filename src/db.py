import sqlite3
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    merchant TEXT NOT NULL,
    amount REAL NOT NULL,
    abs_amount REAL NOT NULL,
    category TEXT NOT NULL,
    UNIQUE (date, merchant, amount)
);
"""
INSERT = """
INSERT OR IGNORE INTO transactions
(date, merchant, amount, abs_amount, category)
VALUES (?, ?, ?, ?, ?);
"""
GET_ALL_TRANSACTIONS = "SELECT * FROM transactions;"
GET_BY_CATEGORY = "SELECT * FROM transactions WHERE category = ?;"
GET_COUNT = "SELECT COUNT(*) AS n FROM transactions;"
GET_MIN_MAX_DATES = "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM transactions;"
GET_CATEGORY_SUMMARY = """
SELECT category, COUNT(*) AS n, SUM(abs_amount) AS total
FROM transactions
WHERE category != 'Income'
GROUP BY category
ORDER BY total DESC;
"""
DROP_TABLE = "DROP TABLE IF EXISTS transactions;"
def connect():
    conn = sqlite3.connect("data/finance.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    with connect() as connection:
        connection.execute(CREATE_TABLE)
def insert_transactions(rows: list[dict]) -> int:
    values = [
        (
            row["date"],
            row["merchant"],
            row["amount"],
            row["abs_amount"],
            row["category"],
        )
        for row in rows
    ]
    with connect() as connection:
        cursor = connection.executemany(INSERT, values)
    return len(values)
def fetch_all_transactions():
    with connect() as connection:
        return connection.execute(GET_ALL_TRANSACTIONS).fetchall()
def fetch_by_category(category):
    with connect() as connection:
        return connection.execute(GET_BY_CATEGORY, (category,)).fetchall()
def db_stats():
    with connect() as conn:
        n = conn.execute(GET_COUNT).fetchone()["n"]
        dates = conn.execute(GET_MIN_MAX_DATES).fetchone()
        return {
            "rows_in_db": n,
            "min_date": dates["min_date"],
            "max_date": dates["max_date"],
        }

def category_summary_sql(limit: int = 10):
    with connect() as conn:
        rows = conn.execute(GET_CATEGORY_SUMMARY).fetchall()
        out = [dict(r) for r in rows[:limit]]
        return out
def reset_db():
    with connect() as conn:
        conn.execute(DROP_TABLE)
    init_db()