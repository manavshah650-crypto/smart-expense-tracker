
import sqlite3
import pandas as pd

DB_NAME = "expenses.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_transaction(title, amount, category, transaction_type, date):
    conn = get_connection()
    conn.execute("""
        INSERT INTO transactions
        (title, amount, category, transaction_type, date)
        VALUES (?, ?, ?, ?, ?)
    """, (title, amount, category, transaction_type, str(date)))
    conn.commit()
    conn.close()


def get_transactions():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY date DESC",
        conn
    )
    conn.close()
    return df


def delete_transaction(transaction_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )
    conn.commit()
    conn.close()


def update_transaction(transaction_id, title, amount,
                       category, transaction_type, date):
    conn = get_connection()
    conn.execute("""
        UPDATE transactions
        SET title = ?, amount = ?, category = ?,
            transaction_type = ?, date = ?
        WHERE id = ?
    """, (title, amount, category, transaction_type,
          str(date), transaction_id))
    conn.commit()
    conn.close()


def save_budget(month, amount):
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO budgets (month, amount)
        VALUES (?, ?)
    """, (month, amount))
    conn.commit()
    conn.close()


def get_budget(month):
    conn = get_connection()
    result = conn.execute(
        "SELECT amount FROM budgets WHERE month = ?",
        (month,)
    ).fetchone()
    conn.close()
    return result[0] if result else 0


def get_monthly_expenses(month):
    conn = get_connection()
    result = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE transaction_type = 'Expense'
        AND substr(date, 1, 7) = ?
    """, (month,)).fetchone()
    conn.close()
    return result[0]


init_db()
