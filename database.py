# database.py
import sqlite3
from datetime import datetime, date, timedelta

DB_NAME = "expenses.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Transactions table: both expenses and income
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            t_date TEXT NOT NULL,
            t_type TEXT NOT NULL,          -- 'expense' or 'income'
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        )
        """
    )

    # Goals table: one row per goal_type ('monthly', 'weekly')
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            goal_type TEXT PRIMARY KEY,    -- 'monthly' or 'weekly'
            amount REAL NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def add_transaction(t_type, amount, category, t_date=None, note=""):
    if t_date is None:
        t_date = date.today().isoformat()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (t_date, t_type, category, amount, note) "
        "VALUES (?, ?, ?, ?, ?)",
        (t_date, t_type, category, amount, note),
    )
    conn.commit()
    conn.close()


def get_all_transactions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, t_date, t_type, category, amount, note "
        "FROM transactions ORDER BY t_date DESC, id DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_summary():
    """Returns total_income, total_expense, balance."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE t_type='income'")
    total_income = cur.fetchone()[0] or 0

    cur.execute("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE t_type='expense'")
    total_expense = cur.fetchone()[0] or 0

    balance = total_income - total_expense
    conn.close()
    return total_income, total_expense, balance


def set_goal(goal_type, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO goals (goal_type, amount)
        VALUES (?, ?)
        ON CONFLICT(goal_type) DO UPDATE SET amount=excluded.amount
        """,
        (goal_type, amount),
    )
    conn.commit()
    conn.close()


def get_goal(goal_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT amount FROM goals WHERE goal_type=?", (goal_type,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def _get_date_range_for_goal(goal_type):
    today = date.today()
    if goal_type == "monthly":
        start = today.replace(day=1)
        # end is today
        end = today
    elif goal_type == "weekly":
        # assume week starts on Monday
        start = today - timedelta(days=today.weekday())
        end = today
    else:
        start = end = today
    return start, end


def get_goal_progress(goal_type):
    """Returns (goal_amount, spent, remaining, status_message)."""
    goal_amount = get_goal(goal_type)
    if goal_amount is None:
        return None, 0.0, 0.0, "No goal set."

    start, end = _get_date_range_for_goal(goal_type)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT IFNULL(SUM(amount), 0)
        FROM transactions
        WHERE t_type='expense'
        AND DATE(t_date) BETWEEN DATE(?) AND DATE(?)
        """,
        (start.isoformat(), end.isoformat()),
    )
    spent = cur.fetchone()[0] or 0.0
    conn.close()

    remaining = goal_amount - spent
    if remaining < 0:
        status = f"You exceeded your {goal_type} limit by {abs(remaining):.2f}."
    elif remaining <= 0.2 * goal_amount:
        status = f"You are close to your {goal_type} limit. Remaining: {remaining:.2f}."
    else:
        status = f"Within your {goal_type} limit. Remaining: {remaining:.2f}."

    return goal_amount, spent, remaining, status
